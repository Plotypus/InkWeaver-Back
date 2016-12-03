from.GenericHandler import *

import loom.database

from inspect import signature
from tornado.ioloop import IOLoop
from typing import Dict

JSON = Dict


class LoomWSError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return '{}: {}'.format(type(self), self.message)


class LoomWSUnimplementedError(LoomWSError):
    """
    Raised when a connection attempts an unimplemented task.
    """
    pass


class LoomWSBadArgumentsError(LoomWSError):
    """
    Raised when necessary arguments were omitted or formatted incorrectly.
    """
    pass


class LoomHandler(GenericHandler):
    def open(self):
        super().open()
        # By default, small messages are coalesced. This can cause delay. We don't want delay.
        self.set_nodelay(True)
        self.user = None
        self.stories = None
        self.wikis = None
        self.story = None
        self.chapters = None
        self.chapter = None
        self.paragraphs = None

    def on_failure(self, reply_to=None, reason=None, **fields):
        response = {
            'success': False,
            'reason':  reason,
        }
        if reply_to is not None:
            response['reply_to'] = reply_to
        response.update(fields)
        json = self.encode_json(response)
        self.write_message(json)

    def write_json(self, data: dict):
        json_string = self.encode_json(data)
        self.write_message(json_string)

    def _get_id_for_client_from_stories(self, story_id):
        for c_id, s_id in self.stories.items():
            if s_id == story_id:
                return c_id
        raise ValueError("{} does not exist in stories".format(story_id))

    def _get_id_for_client_from_wikis(self, wiki_id):
        for c_id, w_id in self.wikis.items():
            if w_id == wiki_id:
                return c_id
        raise ValueError("{} does not exist in wikis".format(wiki_id))

    async def _create_story_ids_mapping(self):
        story_summaries = []
        for story_id in self.user['stories']:
            summary = await loom.database.get_story_summary(story_id)
            story_summaries.append(summary)
        self.stories = {rand_id: story_summary for (rand_id, story_summary) in enumerate(story_summaries)}

    async def _create_wiki_ids_mapping(self):
        # TODO: Uncomment when wikis are implemented
        # wiki_summaries = []
        # for wiki_id in self.user['wikis']:
        #     summary = await loom.database.get_wiki_summary(wiki_id)
        #     wiki_summaries.append(summary)
        # self.wikis = {rand_id: wiki_summary for (rand_id, wiki_summary) in enumerate(wiki_summaries)}
        self.wikis = {rand_id: wiki_id for (rand_id, wiki_id) in enumerate(self.user['wikis'])}

    async def _create_chapter_ids_mapping(self):
        chapter_summaries = await loom.database.get_all_chapter_summaries(self.story['_id'])
        self.chapters = {rand_id: chapter_summary for (rand_id, chapter_summary) in enumerate(chapter_summaries)}

    async def _create_paragraph_ids_mapping(self):
        paragraph_summaries = await loom.database.get_all_paragraph_summaries(self.chapter['_id'])
        self.paragraphs = {rand_id: para_summary for (rand_id, para_summary) in enumerate(paragraph_summaries)}

    def _get_story_summaries(self):
        summaries = []
        for c_id, summary in self.stories.items():
            # Replace the database id with the mapped id
            summary_copy = summary.copy()
            summary_copy['id'] = c_id
            summaries.append(summary_copy)
        return summaries

    def _get_wiki_summaries(self):
        # TODO: Uncomment when wikis are implemented
        # summaries = []
        # for c_id, summary in self.wikis.items():
        #     # Replace the database id with the mapped id
        #     summary_copy = summary.copy()
        #     summary_copy['id'] = c_id
        #     summaries.append(summary_copy)
        # return summaries
        return self.wikis.keys()

    def _get_chapter_summaries(self):
        summaries = []
        for c_id, summary in self.chapters.items():
            summary_copy = summary.copy()
            summary_copy['id'] = c_id
            summaries.append(summary_copy)
        return summaries

    def _get_paragraph_summaries(self):
        summaries = []
        for c_id, summary in self.paragraphs.items():
            summary_copy = summary.copy()
            summary_copy['id'] = c_id
            summaries.append(summary_copy)
        return summaries

    def _format_story_response(self, message_id, story):
        client_wiki_id = self._get_id_for_client_from_wikis(story['wiki_id'])
        data = {
            'reply_to':         message_id,
            'title':            story['title'],
            # 'owner':            self.story['owner'],
            # 'coauthors':        self.story['collaborators'],
            'owner':            None,  # TODO: Resolve these
            'coauthors':        None,
            'statistics':       story['statistics'],
            'settings':         story['settings'],
            'synopsis':         story['synopsis'],
            'wiki':             client_wiki_id,
        }
        return data

    def _format_chapter_response(self, message_id, chapter):
        data = {
            'reply_to':     message_id,
            'title':        chapter['title'],
            'statistics':   chapter['statistics'],
        }
        return data

    def on_message(self, message):
        # TODO: Remove this.
        super().on_message(message)
        try:
            json = self.decode_json(message)
        except:
            self.on_failure(reason="Message received was not valid JSON.", received_message=message)
            return
        # on_message may not be a coroutine (as of Tornado 4.3).
        # To work around this, we call spawn_callback to start a coroutine.
        # However, this results in errors not propagating back up.
        # Side effect: More messages may be received before the one below is fully executed.
        # See:
        #   https://stackoverflow.com/questions/35542864/how-to-use-python-3-5-style-async-and-await-in-tornado-for-websockets
        # And:
        #   http://stackoverflow.com/questions/33723830/exception-ignored-in-tornado-websocket-on-message-method
        IOLoop.current().spawn_callback(self.handle_message, json)

    async def handle_message(self, message: JSON):
        message_id = message.get('message_id', None)
        try:
            action = message.pop('action')
        except KeyError:
            self.on_failure(reply_to=message_id, reason="`action` field not supplied")
            return
        try:
            await self.dispatch(message, action, message_id)
        except LoomWSUnimplementedError:
            err_message = "invalid `action`: {}".format(action)
            self.on_failure(reply_to=message_id, reason=err_message)
        except LoomWSBadArgumentsError as e:
            self.on_failure(reply_to=message_id, reason=e.message)

    async def dispatch(self, message: JSON, action: str, message_id=None):
        try:
            func = self.DISPATCH[action]
            try:
                return await func(self, **message)
            except TypeError:
                # Most likely, the wrong arguments were given.
                # We do some introspection to give back useful error messages.
                sig = signature(func)
                # The first assumption is that not all of the necessary arguments were given, so check for that.
                missing_fields = []
                print("params: {}".format(signature(func).parameters.values()))
                for param in filter(lambda p: p.name != 'self' and p.kind == p.POSITIONAL_OR_KEYWORD and p.default == p.empty, sig.parameters.values()):
                    if param.name not in message:
                        missing_fields.append(param.name)
                if missing_fields:
                    # So something *was* missing!
                    message = "request of type '{}' missing fields: {}".format(action, missing_fields)
                    raise LoomWSBadArgumentsError(message)
                else:
                    # Something else has gone wrong...
                    # Let's check if too many arguments were given.
                    num_required_arguments = len(sig.parameters) - 1  # We subtract 1 for `self`.
                    num_given_arguments = len(message)
                    if num_required_arguments != num_given_arguments:
                        # Yep, they gave the wrong number. Let them know.
                        # We don't check them all because somebody could create a large JSON with an absurd number of
                        # arguments and we'd spend cycles counting them all... easy DOS.
                        raise LoomWSBadArgumentsError("too many fields given for request of type '{}'".format(action))
                    else:
                        # It was something else entirely.
                        raise
        except KeyError:
            # The method is not implemented.
            raise LoomWSUnimplementedError

    async def get_user_info(self, message_id):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        data = {
            'reply_to':         message_id,
            'username':         self.user['username'],
            'avatar':           self.user['avatar'],
            'email':            self.user['email'],
            'name':             self.user['name'],
            'pen_name':         self.user['pen_name'],
            'stories':          self._get_story_summaries(),
            'wikis':            self._get_wiki_summaries(),
            'bio':              self.user['bio'],
            'statistics':       self.user['statistics'],
            'preferences':      self.user['preferences'],
        }
        self.write_json(data)

    async def load_story(self, message_id, story):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        story_summary = self.stories.get(story)
        if story_summary:
            story_id = story_summary['id']
            self.story = await loom.database.get_story(story_id)
            data = self._format_story_response(message_id, self.story)
            self.write_json(data)
        else:
            self.on_failure(message_id, "Story does not exist")

    async def get_chapters(self, message_id):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        # TODO: Raise an error if user hasn't loaded a story
        if self.story is None:
            self.on_failure(message_id, "No story loaded")
            return
        await self._create_chapter_ids_mapping()
        chapter_summaries = self._get_chapter_summaries()
        data = {
            'reply_to': message_id,
            'chapters': chapter_summaries,
        }
        self.write_json(data)

    async def load_story_with_chapters(self, message_id, story):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        story_summary = self.stories.get(story)
        if story_summary:
            story_id = story_summary['id']
            self.story = await loom.database.get_story(story_id)
            data = self._format_story_response(message_id, self.story)
            await self._create_chapter_ids_mapping()
            chapter_summaries = self._get_chapter_summaries()
            data['chapters'] = chapter_summaries
            self.write_json(data)
        else:
            self.on_failure(message_id, "Story does not exist")

    async def load_chapter(self, message_id, chapter):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        # TODO: Raise an error if user hasn't loaded a story
        if self.story is None:
            self.on_failure(message_id, "No story loaded")
            return
        chapter_summary = self.chapters.get(chapter)
        if chapter_summary:
            chapter_id = chapter_summary['id']
            self.chapter = await loom.database.get_chapter(chapter_id)
            data = self._format_chapter_response(message_id, self.chapter)
            self.write_json(data)
        else:
            self.on_failure(message_id, "Chapter does not exist")

    async def get_paragraphs(self, message_id):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        # TODO: Raise an error if user hasn't loaded a story
        if self.story is None:
            self.on_failure(message_id, "No story loaded")
            return
        # TODO: Raise an error if user hasn't loaded a chapter
        if self.chapter is None:
            self.on_failure(message_id, "No chapter loaded")
            return
        await self._create_paragraph_ids_mapping()
        paragraph_summaries = self._get_paragraph_summaries()
        data = {
            'reply_to': message_id,
            'paragraphs': paragraph_summaries,
        }
        self.write_json(data)

    async def load_chapter_with_paragraphs(self, message_id, chapter):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        # TODO: Raise an error if user hasn't loaded a story
        if self.story is None:
            self.on_failure(message_id, "No story loaded")
            return
        chapter_summary = self.chapters.get(chapter)
        if chapter_summary:
            chapter_id = chapter_summary['id']
            self.chapter = await loom.database.get_chapter(chapter_id)
            data = self._format_chapter_response(message_id, self.chapter)
            await self._create_paragraph_ids_mapping()
            paragraph_summaries = self._get_paragraph_summaries()
            data['paragraphs'] = paragraph_summaries
            self.write_json(data)
        else:
            self.on_failure(message_id, "Chapter does not exist")

    async def load_paragraph(self, message_id, paragraph):
        pass

    async def load_paragraph_with_text(self, message_id, paragraph):
        raise LoomWSUnimplementedError

    async def create_story(self, message_id, story):
        # TODO: Raise an error if user is not logged in/authenticated at this point
        if self.user is None:
            self.on_failure(message_id, "Not logged in")
            return
        user_id = self.user['_id']
        wiki_id = self.wikis[story['wiki']]
        title = story['title']
        publication_name = story['publication_name']
        synopsis = story.get('synopsis', None)
        story_id = await loom.database.create_story(user_id,wiki_id, title, publication_name, synopsis)
        # TODO: Come up with a better way to 'id' new story
        # TODO: Add story to self.user and self.stories
        self.stories[len(self.stories)] = story_id
        self.story = await loom.database.get_story(story_id)
        data = await self._format_story_response(message_id, self.story)
        self.write_json(data)

    async def create_chapter(self, message_id, title):
        pass

    async def create_end_chapter(self, message_id, title):
        pass

    async def create_paragraph(self, message_id):
        pass

    async def create_end_paragraph(self, message_id):
        pass

    async def update_story(self, message_id, story, changes):
        pass

    async def update_current_story(self, message_id, changes):
        pass

    async def update_chapter(self, message_id, chapter, changes):
        pass

    async def update_current_chapter(self, message_id, changes):
        pass

    async def update_paragraph(self, message_id, paragraph, changes):
        raise LoomWSUnimplementedError

    async def replace_paragraph(self, message_id, text):
        pass

    async def delete_story(self, message_id, story):
        pass

    async def delete_current_story(self, message_id):
        pass

    async def delete_chapter(self, message_id, chapter):
        pass

    async def delete_current_chapter(self, message_id):
        pass

    async def delete_paragraph(self, message_id, paragraph):
        pass

    async def delete_current_paragraph(self, message_id):
        pass

    DISPATCH = {
        'get_user_info':                get_user_info,
        'load_story':                   load_story,
        'get_chapters':                 get_chapters,
        'load_story_with_chapters':     load_story_with_chapters,
        'load_chapter':                 load_chapter,
        'get_paragraphs':               get_paragraphs,
        'load_chapter_with_paragraphs': load_chapter_with_paragraphs,
        'load_paragraph':               load_paragraph,
        'load_paragraph_with_text':     load_paragraph_with_text,
        'create_story':                 create_story,
        'create_chapter':               create_chapter,
        'create_end_chapter':           create_end_chapter,
        'create_paragraph':             create_paragraph,
        'create_end_paragraph':         create_end_paragraph,
        'update_story':                 update_story,
        'update_current_story':         update_current_story,
        'update_chapter':               update_chapter,
        'update_current_chapter':       update_current_chapter,
        'update_paragraph':             update_paragraph,
        'replace_paragraph':            replace_paragraph,
        'delete_story':                 delete_story,
        'delete_current_story':         delete_current_story,
        'delete_chapter':               delete_chapter,
        'delete_current_chapter':       delete_current_chapter,
        'delete_paragraph':             delete_paragraph,
        'delete_current_paragraph':     delete_current_paragraph,
    }
