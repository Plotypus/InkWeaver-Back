from .abstract_interface import AbstractDBInterface
from .errors import *

from loom.database.clients import *
from loom.serialize import decode_string_to_bson, encode_bson_to_string

import nltk
import re

from bson.objectid import ObjectId
from collections import Counter, defaultdict
from itertools import chain
from os.path import dirname, join as pathjoin
from string import punctuation
from typing import ClassVar

# Adjust the NLTK path.
nltk.data.path.insert(0, pathjoin(dirname(dirname(dirname(__file__))), 'nltk_data'))

CREATE_LINK_REGEX = re.compile(r'{#\|(.*?)\|#}')


def generate_link_format_regex():
    o = ObjectId()
    inner_regex = r'[a-f\d]{24}'
    bson_string = encode_bson_to_string(o)
    # Strip the whitespace in the encoding and allow one or more spaces.
    # Note: re.escape also escapes spaces, which is why the replace looks for '\\ '.
    pattern = re.escape(bson_string).replace(str(o), inner_regex).replace('\\ ', r'\s*')
    return re.compile(pattern)


class MongoDBInterface(AbstractDBInterface):
    def __init__(self, db_client_class: ClassVar, db_name, db_host, db_port, db_user=None, db_pass=None):
        if not issubclass(db_client_class, MongoDBClient):
            raise ValueError("invalid MongoDB client class: {}".format(db_client_class.__name__))  # pragma: no cover
        self._client = db_client_class(db_name, db_host, db_port, db_user, db_pass)
        self._link_format_regex = generate_link_format_regex()

    @property
    def client(self) -> MongoDBClient:
        return self._client

    @property
    def host(self):
        return self.client.host

    @property
    def port(self):
        return self.client.port

    @property
    def link_format_regex(self):
        return self._link_format_regex

    ###########################################################################
    #
    # Database Methods
    #
    ###########################################################################

    async def authenticate_client(self, username, password):
        await self.client.authenticate(username, password)

    async def drop_database(self):
        await self.client.drop_database()

    async def drop_all_collections(self):
        await self.client.drop_all_collections()

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    async def create_user(self, username, password, name, email, bio=None):
        if await self.client.username_exists(username):
            raise ValueError('Username is already taken.')
        if await self.client.email_exists(email):
            raise ValueError('Email is already taken.')
        password_hash = super().hash_password(password)
        inserted_id = await self.client.create_user(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            bio=bio,
            avatar=None
        )
        return inserted_id

    async def password_is_valid_for_username(self, username, password):
        try:
            stored_hash = await self.client.get_password_hash_for_username(username)
        except ClientError:
            return False
        else:
            return super().verify_hash(password, stored_hash)

    async def get_user_id_for_username(self, username):
        try:
            user_id = await self.client.get_user_id_for_username(username)
        except ClientError:
            raise BadValueError(query='get_user_id_for_username', value=username)
        else:
            return user_id

    async def get_user_preferences(self, user_id):
        try:
            preferences = await self.client.get_user_preferences(user_id)
        except ClientError:
            raise BadValueError(query='get_user_preferences', value=user_id)
        else:
            return preferences

    async def get_user_stories_and_wikis(self, user_id):
        try:
            story_ids_and_positions = await self.client.get_user_stories(user_id)
        except ClientError:
            raise BadValueError(query='get_user_stories_and_wikis', value=user_id)
        try:
            wiki_ids = await self.client.get_user_wiki_ids(user_id)
        except ClientError:
            raise BadValueError(query='get_user_stories_and_wikis', value=user_id)
        wiki_ids_to_titles = {}
        wikis = []
        for wiki_id in wiki_ids:
            try:
                wiki = await self.client.get_wiki(wiki_id)
            except ClientError:
                raise BadValueError(query='get_user_stories_and_wikis', value=wiki_id)
            wiki_ids_to_titles[wiki_id] = wiki['title']
            access_level = self._get_current_user_access_level_in_object(user_id, wiki)
            wikis.append({
                'wiki_id':      wiki_id,
                'title':        wiki['title'],
                'access_level': access_level,
            })
        stories = []
        for story_id_and_pos in story_ids_and_positions:
            story_id = story_id_and_pos['story_id']
            last_pos = story_id_and_pos['position_context']
            try:
                story = await self.client.get_story(story_id)
            except ClientError:
                raise BadValueError(query='get_user_stories_and_wikis', value=story_id)
            access_level = self._get_current_user_access_level_in_object(user_id, story)
            wiki_title = wiki_ids_to_titles[story['wiki_id']]
            stories.append({
                'story_id': story_id,
                'title': story['title'],
                'wiki_summary': {'wiki_id': story['wiki_id'], 'title': wiki_title},
                'access_level': access_level,
                'position_context': last_pos,
            })
        return {'stories': stories, 'wikis': wikis}

    @staticmethod
    def _get_current_user_access_level_in_object(user_id, obj):
        for user in obj['users']:
            if user['user_id'] == user_id:
                return user['access_level']

    async def set_user_password(self, user_id, password):
        # TODO: Check the password is not equal to the previous password.
        # Maybe even check that it's not too similar, like:
        #   https://security.stackexchange.com/questions/53481/does-facebook-store-plain-text-passwords
        password_hash = super().hash_password(password)
        try:
            await self.client.set_user_password_hash(user_id, password_hash)
        except ClientError:
            raise FailedUpdateError(query='set_user_password')

    async def set_user_name(self, user_id, name):
        try:
            await self.client.set_user_name(user_id, name)
        except ClientError:
            raise FailedUpdateError(query='set_user_name')

    async def set_user_email(self, user_id, email):
        # TODO: Check user doesn't use an email that somebody else is using.
        # TODO: Check email address is properly formed.
        try:
            await self.client.set_user_email(user_id, email)
        except ClientError:
            raise FailedUpdateError(query='set_user_email')

    async def set_user_bio(self, user_id, bio):
        try:
            await self.client.set_user_bio(user_id, bio)
        except ClientError:
            raise FailedUpdateError(query='set_user_bio')

    async def set_user_avatar(self, user_id, avatar):
        try:
            await self.client.set_user_avatar(user_id, avatar)
        except ClientError:
            raise FailedUpdateError(query='set_user_avatar')

    async def set_story_position_context(self, user_id, story_id, position_context):
        try:
            await self.client.set_user_story_position_context(user_id, story_id, position_context)
        except ClientError:
            raise FailedUpdateError(query='set_story_position_context')

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    async def create_story(self, user_id, title, summary, wiki_id) -> ObjectId:
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        section_id = await self.create_section(title)
        await self.add_paragraph(section_id, summary)
        inserted_id = await self.client.create_story(title, wiki_id, user_description, section_id)
        try:
            await self.client.add_story_to_user(user_id, inserted_id)
        except ClientError:
            raise FailedUpdateError(query='create_story')
        else:
            return inserted_id

    async def create_section(self, title) -> ObjectId:
        inserted_id = await self.client.create_section(title)
        return inserted_id

    async def add_preceding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_preceding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
            raise FailedUpdateError(query='add_preceding_subsection')
        else:
            return subsection_id

    async def add_inner_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_inner_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
            raise FailedUpdateError(query='add_inner_subsection')
        else:
            return subsection_id

    async def add_succeeding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_succeeding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
            raise FailedUpdateError(query='add_succeeding_subsection')
        else:
            return subsection_id

    async def add_paragraph(self, section_id, text, succeeding_paragraph_id=None):
        try:
            paragraph_ids = await self.client.get_paragraph_ids(section_id)
        except ClientError:
            raise BadValueError(query='add_paragraph', value=section_id)
        try:
            if not succeeding_paragraph_id:
                index = None
            else:
                index = paragraph_ids.index(succeeding_paragraph_id)
        except ValueError:
            raise BadValueError(query='add_paragraph', value=succeeding_paragraph_id)
        paragraph_id = ObjectId()
        try:
            await self.client.insert_paragraph(paragraph_id, '', to_section_id=section_id, at_index=index)
        except ClientError:
            raise FailedUpdateError(query='add_paragraph')
        try:
            await self.client.insert_links_for_paragraph(paragraph_id, list(), in_section_id=section_id, at_index=index)
        except ClientError:
            raise FailedUpdateError(query='add_paragraph')
        # Default the note to None
        try:
            await self.client.insert_note_for_paragraph(paragraph_id, in_section_id=section_id, note=None,
                                                        at_index=index)
        except ClientError:
            raise FailedUpdateError(query='add_paragraph')
        if text is not None:
            links_created = await self.set_paragraph_text(section_id, text, paragraph_id)
        else:
            links_created = []
        return paragraph_id, links_created

    async def add_bookmark(self, name, story_id, section_id, paragraph_id, index=None):
        bookmark_id = ObjectId()
        try:
            await self.client.insert_bookmark(bookmark_id, story_id, section_id, paragraph_id, name, index)
        except ClientError:
            raise FailedUpdateError(query='add_bookmark')
        else:
            return bookmark_id

    async def get_story(self, story_id):
        try:
            story = await self.client.get_story(story_id)
        except ClientError:
            raise BadValueError(query='get_story', value=story_id)
        else:
            return story

    async def get_story_bookmarks(self, story_id):
        try:
            story = await self.client.get_story(story_id)
        except ClientError:
            raise BadValueError(query='get_story_bookmarks', value=story_id)
        else:
            return story['bookmarks']

    async def get_story_hierarchy(self, story_id):
        try:
            story = await self.get_story(story_id)
        except ClientError:
            raise BadValueError(query='get_story_hierarchy', value=story_id)
        section_id = story['section_id']
        return await self.get_section_hierarchy(section_id)

    async def get_section_hierarchy(self, section_id):
        try:
            section = await self.client.get_section(section_id)
        except ClientError:
            raise BadValueError(query='get_section_hierarchy', value=section_id)
        hierarchy = {
            'title':      section['title'],
            'section_id': section_id,
            'preceding_subsections':
                [await self.get_section_hierarchy(pre_sec_id) for pre_sec_id in section['preceding_subsections']],
            'inner_subsections':
                [await self.get_section_hierarchy(sec_id) for sec_id in section['inner_subsections']],
            'succeeding_subsections':
                [await self.get_section_hierarchy(post_sec_id) for post_sec_id in section['succeeding_subsections']],
        }
        return hierarchy

    async def get_section_content(self, section_id):
        try:
            section = await self.client.get_section(section_id)
        except ClientError:
            raise BadValueError(query='get_section_content', value=section_id)
        paragraphs = []
        for db_paragraph, db_note in zip(section['content'], section['notes']):
            def join_dictionaries_and_return(paragraph, note):
                paragraph.update(note)
                return paragraph
            paragraphs.append(join_dictionaries_and_return(db_paragraph, db_note))
        return paragraphs

    async def set_story_title(self, story_id, title):
        try:
            story = await self.client.get_story(story_id)
        except ClientError:
            raise BadValueError(query='set_story_title', value=story_id)
        try:
            await self.client.set_story_title(story_id, title)
        except ClientError:
            raise FailedUpdateError(query='set_story_title')
        try:
            await self.client.set_section_title(story['section_id'], title)
        except ClientError:
            raise FailedUpdateError(query='set_story_title')

    async def set_section_title(self, section_id, title):
        try:
            await self.client.set_section_title(section_id, title)
        except ClientError:
            raise FailedUpdateError(query='set_section_title')

    async def set_paragraph_text(self, section_id, text, paragraph_id):
        text, links_created = await self._find_and_create_links_in_paragraph(section_id, paragraph_id, text)
        sentences_and_links, word_frequencies = await self.get_links_and_word_counts_from_paragraph(text)
        page_updates = {}
        section_links = []
        for sentence, links in sentences_and_links:
            for link in links:
                link_id = link['_id']
                context = link['context']
                context['paragraph_id'] = paragraph_id
                context['text'] = sentence
                # Update context in link.
                try:
                    await self.client.set_link_context(link_id, context)
                except ClientError:
                    raise FailedUpdateError(query='set_paragraph_text')
                # Get page ID from link and add its context to `page_updates`.
                page_id = link['page_id']
                link_updates = page_updates.get(page_id)
                if link_updates is None:
                    link_updates = {}
                    page_updates[page_id] = link_updates
                link_updates[link_id] = context
                # Add link to `section_links` to update the links for the paragraph.
                section_links.append(link_id)
        # Apply updates to references in pages.
        for page_id, updates in page_updates.items():
            try:
                page = await self.client.get_page(page_id)
            except ClientError:
                raise BadValueError(query='set_paragraph_text', value=page_id)
            references = page['references']
            for link_id, context in updates.items():
                self._update_link_in_references_with_context(references, link_id, context)
            try:
                await self.client.set_page_references(page_id, references)
            except ClientError:
                raise FailedUpdateError(query='set_paragraph_text')
        # Update links for this paragraph for the section.
        try:
            await self.client.set_links_in_section(section_id, section_links, paragraph_id)
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        try:
            await self.client.set_paragraph_text(paragraph_id, text, in_section_id=section_id)
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        # Get statistics for section and paragraph
        try:
            section_stats = await self.client.get_section_statistics(section_id)
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        section_wf = Counter(section_stats['word_frequency'])
        try:
            paragraph_stats = await self.client.get_paragraph_statistics(section_id, paragraph_id)
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        paragraph_wf = Counter(paragraph_stats['word_frequency'])
        # Update statistics for section and paragraph
        section_wf.subtract(paragraph_wf)
        section_wf.update(word_frequencies)
        try:
            await self.client.set_section_statistics(section_id, section_wf, sum(section_wf.values()))
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        try:
            await self.client.set_paragraph_statistics(paragraph_id, word_frequencies, sum(word_frequencies.values()),
                                                       section_id)
        except ClientError:
            raise FailedUpdateError(query='set_paragraph_text')
        return links_created

    @staticmethod
    def _update_link_in_references_with_context(references, link_id, context):
        for reference in references:
            if reference['link_id'] == link_id:
                reference['context'] = context
                break

    async def get_links_and_word_counts_from_paragraph(self, paragraph_text):
        # TODO: Support languages other than English.
        sentences = nltk.sent_tokenize(paragraph_text)
        word_counts = Counter()
        results = []
        for sentence in sentences:
            sentence_links = []
            links_replaced_sentence = sentence
            link_matches = re.findall(self.link_format_regex, sentence)
            for match in link_matches:
                potential_id = decode_string_to_bson(match)
                try:
                    link = await self.get_link(potential_id)
                except InterfaceError:
                    # `potential_id` looked like a link, but it did not correspond to any legitimate link.
                    continue
                try:
                    alias = await self.client.get_alias(link['alias_id'])
                except ClientError:
                    raise BadValueError(query='get_links_and_word_counts_from_paragraph', value=potential_id)
                replacement = alias['name']
                links_replaced_sentence = links_replaced_sentence.replace(match, replacement)
                sentence_links.append(link)
            # Mongo does not support '$' or '.' in key name, so we replace them with their unicode equivalents.
            words = [token.replace('.', '').replace('$', '').lower() for token in
                     nltk.word_tokenize(links_replaced_sentence) if token not in punctuation]
            word_counts.update(words)
            if sentence_links:
                sentence_tuple = (sentence, sentence_links)
                results.append(sentence_tuple)
        return results, word_counts

    async def _find_and_create_links_in_paragraph(self, section_id, paragraph_id, text):
        prev_end = 0
        links_created = []  # (link_id, page_id, name)
        # Buffer used for efficiently joining the string back together.
        buffer = []
        # Iterate through each encoded request and replace with a link_id.
        for match in CREATE_LINK_REGEX.finditer(text):
            start, end = match.span()
            link_id, page_id, name = await self._create_link_and_replace_text(section_id, paragraph_id, text, start,
                                                                              end)
            links_created.append((link_id, page_id, name))
            # Strip out the space in the encoding.
            encoded_link_id = encode_bson_to_string(link_id).replace(' ', '')
            # Add the previous text and link_id to the buffer.
            buffer.append(text[prev_end:start])
            buffer.append(encoded_link_id)
            prev_end = end
        # Don't forget to add the rest of the string.
        buffer.append(text[prev_end:])
        return ''.join(buffer), links_created

    async def _create_link_and_replace_text(self, section_id, paragraph_id, text, start, end):
        # Get the match and split it into story_id, page_id, and name.
        tokens = text[start:end].split('|')[1:4]
        story_id, page_id, name = tuple(tokens)
        # Convert oids from strings to ObjectId.
        story_id = decode_string_to_bson(story_id)
        page_id = decode_string_to_bson(page_id)
        link_id = await self.create_link(story_id, section_id, paragraph_id, name, page_id)
        return link_id, page_id, name

    async def set_bookmark_name(self, story_id, bookmark_id, new_name):
        try:
            await self.client.set_bookmark_name(story_id, bookmark_id, new_name)
        except ClientError:
            raise FailedUpdateError(query='set_bookmark_name')

    async def set_note(self, section_id, paragraph_id, text):
        try:
            await self.client.set_note(section_id, paragraph_id, text)
        except ClientError:
            raise FailedUpdateError(query='set_note')

    async def delete_story(self, story_id):
        try:
            story = await self.get_story(story_id)
        except ClientError:
            raise BadValueError(query='delete_story', value=story_id)
        section_id = story['section_id']
        await self.recur_delete_section_and_subsections(section_id)
        for user in story['users']:
            user_id = user['user_id']
            try:
                await self.client.remove_story_from_user(user_id, story_id)
            except ClientError:
                raise FailedUpdateError(query='delete_story')
        try:
            await self.client.delete_story(story_id)
        except:
            raise FailedUpdateError(query='delete_story')

    async def delete_section(self, section_id):
        await self.recur_delete_section_and_subsections(section_id)

    async def recur_delete_section_and_subsections(self, section_id):
        try:
            section = await self.client.get_section(section_id)
        except ClientError:
            raise BadValueError(query='recur_delete_section_and_subsections', value=section_id)
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            await self.recur_delete_section_and_subsections(subsection_id)
        for link_summary in section['links']:
            link_ids = link_summary['links']
            for link_id in link_ids:
                await self.delete_link(link_id)
        try:
            await self.client.delete_section(section['_id'])
        except ClientError:
            raise FailedUpdateError(query='recur_delete_sections_and_subsections')
        try:
            await self.client.delete_bookmark_by_section_id(section_id)
        except ClientError:
            raise FailedUpdateError(query='recur_delete_sections_and_subsections')

    async def delete_paragraph(self, section_id, paragraph_id):
        try:
            link_ids = await self.client.get_links_in_paragraph(paragraph_id, section_id)
        except ClientError:
            raise BadValueError(query='delete_paragraph', value=paragraph_id)
        for link_id in link_ids:
            await self.delete_link(link_id)
        try:
            await self.client.delete_paragraph(section_id, paragraph_id)
        except ClientError:
            raise FailedUpdateError(query='delete_paragraph')
        try:
            await self.client.delete_bookmark_by_paragraph_id(paragraph_id)
        except ClientError:
            raise FailedUpdateError(query='delete_paragraph')

    async def delete_note(self, section_id, paragraph_id):
        # To delete a note, we simply set it as an empty-string.
        try:
            await self.client.set_note(section_id, paragraph_id, '')
        except ClientError:
            raise FailedUpdateError(query='delete_note')

    async def delete_bookmark(self, bookmark_id):
        try:
            await self.client.delete_bookmark_by_id(bookmark_id)
        except ClientError:
            raise FailedUpdateError(query='delete_bookmark')

    async def move_subsection_as_preceding(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise BadValueError(query='move_subsection_as_preceding', value=to_parent_id)
        try:
            await self.client.remove_section_from_parent(section_id)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_preceding')
        try:
            await self.client.insert_preceding_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_preceding')

    async def move_subsection_as_inner(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise BadValueError(query='move_subsection_as_inner', value=to_parent_id)
        try:
            await self.client.remove_section_from_parent(section_id)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_inner')
        try:
            await self.client.insert_inner_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_inner')

    async def move_subsection_as_succeeding(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise BadValueError(query='move_subsection_as_succeeding', value=to_parent_id)
        try:
            await self.client.remove_section_from_parent(section_id)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_succeeding')
        try:
            await self.client.insert_succeeding_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_succeeding')

    async def _section_is_ancestor_of_candidate(self, section_id, candidate_section_id):
        if section_id == candidate_section_id:
            return True
        try:
            section = await self.client.get_section(section_id)
        except ClientError:
            raise BadValueError(query='_section_is_ancestor_of_candidate', value=section_id)
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            if await self._section_is_ancestor_of_candidate(subsection_id, candidate_section_id):
                return True
        return False

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, user_id, title, summary):
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        segment_id = await self.create_segment(title)
        inserted_id = await self.client.create_wiki(title, user_description, summary, segment_id)
        try:
            await self.client.add_wiki_to_user(user_id, inserted_id)
        except ClientError:
            raise FailedUpdateError(query='create_wiki')
        else:
            return inserted_id

    async def create_segment(self, title):
        inserted_id = await self.client.create_segment(title)
        return inserted_id

    async def create_page(self, title, in_parent_segment):
        # Create the page and include the `template_headings` from the parent
        parent_segment = await self.get_segment(in_parent_segment)
        template_headings = parent_segment['template_headings']
        page_id = await self.client.create_page(title, template_headings)
        # Create an alias for the page with the title as the alias name
        await self._create_alias(page_id, title)
        try:
            await self.client.insert_page_to_parent_segment(page_id, in_parent_segment, at_index=None)
        except ClientError:
            await self.delete_page(page_id)
            raise FailedUpdateError(query='create_page')
        else:
            return page_id

    async def add_child_segment(self, title, parent_id):
        try:
            parent_segment = await self.client.get_segment(parent_id)
        except ClientError:
            raise BadValueError(query='add_child_segment', value='parent_id')
        template_headings = parent_segment['template_headings']
        child_segment_id = await self.client.create_segment(title, template_headings)
        try:
            await self.client.insert_segment_to_parent_segment(child_segment_id, parent_id, at_index=None)
        except ClientError:
            await self.delete_segment(child_segment_id)
            raise FailedUpdateError(query='add_child_segment')
        else:
            return child_segment_id

    async def add_template_heading(self, title, segment_id):
        # Check to see if a template heading already exists with the same title.
        try:
            await self.client.get_template_heading(title, segment_id)
        except ClientError:
            # Template heading does not exist, which is the desired behavior, so we continue execution.
            pass
        else:
            # Template heading already exists within the segment
            raise BadValueError(query='add_template_heading', value=title)
        # Add the template heading to the segment.
        try:
            await self.client.append_template_heading_to_segment(title, segment_id)
        except ClientError:
            raise FailedUpdateError(query='add_template_heading')

    async def add_heading(self, title, page_id, index=None):
        # Check to see if a heading already exists with the same title.
        try:
            await self.client.get_heading(title, page_id)
        except ClientError:
            # Heading does not exist, which is the desired behavior, so we continue execution.
            pass
        else:
            # Heading already exists within the page
            raise BadValueError(query='add_heading', value=title)
        # Add the heading to the page.
        try:
            await self.client.insert_heading(title, page_id, index)
        except ClientError:
            raise FailedUpdateError(query='add_heading')

    async def get_wiki(self, wiki_id):
        try:
            wiki = await self.client.get_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='get_wiki', value=wiki_id)
        else:
            return wiki

    async def get_wiki_alias_list(self, wiki_id):
        try:
            wiki = await self.get_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='get_wiki_alias_list', value=wiki_id)
        segment_id = wiki['segment_id']
        return await self._get_segment_alias_list(segment_id)

    async def _get_segment_alias_list(self, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='_get_segment_alias_lis', value=segment_id)
        # Get all the alias information for the pages at the current level.
        segment_alias_list = []
        for page_id in segment['pages']:
            for alias_entry in await self._get_page_alias_list(page_id):
                segment_alias_list.append(alias_entry)
        # Then add all child segments' page alias lists to the current list, keeping it flat.
        for segment_id in segment['segments']:
            for page_aliases in await self._get_segment_alias_list(segment_id):
                segment_alias_list.append(page_aliases)
        return segment_alias_list

    async def _get_page_alias_list(self, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='_get_page_alias_list', value=page_id)
        alias_list = []
        for alias_name, alias_id in page['aliases'].items():
            try:
                alias = await self.client.get_alias(alias_id)
            except ClientError:
                raise BadValueError(query='_get_page_alias_list', value=alias_id)
            alias_list.append({
                'alias_name':   alias_name,
                'page_id':      page_id,
                'link_ids':     alias['links'],
            })
        return alias_list

    async def get_wiki_hierarchy(self, wiki_id):
        wiki = await self.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self.get_segment_hierarchy(segment_id)

    async def get_segment_hierarchy(self, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='get_segment_hierarchy', value=segment_id)
        hierarchy = {
            'title':      segment['title'],
            'segment_id': segment_id,
            'segments':   [],
            'pages':      [],
        }
        segments = hierarchy['segments']
        pages = hierarchy['pages']
        # Iterate through the segments, popping out the `links` field and inserting them into the top-level `links`.
        for segment_id in segment['segments']:
            inner_segment = await self.get_segment_hierarchy(segment_id)
            segments.append(inner_segment)
        # Iterate through the pages, pulling the links from the aliases inside of each.
        for page_id in segment['pages']:
            page = await self._get_page_for_hierarchy(page_id)
            pages.append(page)
        return hierarchy

    async def _get_page_for_hierarchy(self, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='_get_page_for_hierarchy', value=page_id)
        else:
            return {
                'title':   page['title'],
                'page_id': page_id,
            }

    async def get_segment(self, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='get_segment', value=segment_id)
        segment['segments'] = [await self.get_segment_summary(child_id) for child_id in segment['segments']]
        segment['pages'] = [await self.get_page_summary(page_id) for page_id in segment['pages']]
        return segment

    async def get_segment_summary(self, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='get_segment_summary', value=segment_id)
        else:
            return {
                'segment_id': segment_id,
                'title':      segment['title'],
            }

    async def get_page(self, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='get_page', value=page_id)
        for reference in page['references']:
            # Take the context from inside the reference and push it to the next level up.
            reference.update(reference.pop('context'))
        return page

    async def get_page_summary(self, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='get_page_summary', value=page_id)
        else:
            return {
                'page_id':   page_id,
                'title':     page['title'],
            }

    async def set_wiki_title(self, title, wiki_id):
        try:
            wiki = await self.client.get_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='set_wiki_title', value=wiki_id)
        try:
            await self.client.set_wiki_title(title, wiki_id)
        except ClientError:
            raise FailedUpdateError(query='set_wiki_title')
        try:
            await self.client.set_segment_title(title, wiki['segment_id'])
        except ClientError:
            raise FailedUpdateError(query='set_wiki_title')

    async def set_segment_title(self, title, segment_id):
        try:
            await self.client.set_segment_title(title, segment_id)
        except ClientError:
            raise FailedUpdateError(query='set_segment_title')

    async def set_template_heading_title(self, old_title, new_title, segment_id):
        try:
            await self.client.set_template_heading_title(old_title, new_title, segment_id)
        except ClientError:
            raise FailedUpdateError(query='set_template_heading_title')

    async def set_template_heading_text(self, title, text, segment_id):
        try:
            await self.client.set_template_heading_text(title, text, segment_id)
        except ClientError:
            raise FailedUpdateError(query='set_template_heading_text')

    async def set_page_title(self, new_title, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='set_page_title', value=page_id)
        old_title = page['title']
        alias_id = page['aliases'][old_title]
        # It's important that we change the page title before renaming the alias
        # Otherwise, we are going to keep creating new aliases
        try:
            await self.client.set_page_title(new_title, page_id)
        except ClientError:
            raise FailedUpdateError(query='set_page_title')
        await self.change_alias_name(alias_id, new_title)
        # Return the `alias_id` to facilitate error handling up above.
        return alias_id

    async def set_heading_title(self, old_title, new_title, page_id):
        # Check to see if a heading already exists with the same title.
        try:
            await self.client.get_heading(new_title, page_id)
        except ClientError:
            # Heading does not exist, which is the desired behavior, so we continue execution.
            pass
        else:
            # Heading already exists within the page
            raise BadValueError(query='set_heading_title', value=new_title)
        try:
            await self.client.set_heading_title(old_title, new_title, page_id)
        except ClientError:
            raise FailedUpdateError(query='set_heading_title')

    async def set_heading_text(self, title, text, page_id):
        try:
            await self.client.set_heading_text(title, text, page_id)
        except ClientError:
            raise FailedUpdateError(query='set_heading_text')

    async def delete_wiki(self, user_id, wiki_id):
        # TODO: Is this the best way to handle this? Should all stories use one new wiki? Should this be an option?
        try:
            wiki = await self.client.get_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='delete_wiki', value=wiki_id)
        # Update each story using this wiki with a new wiki.
        try:
            story_summaries = await self.client.get_summaries_of_stories_using_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='delete_wiki', value=wiki_id)
        for summary in story_summaries:
            story_id = summary['_id']
            title = summary['title']
            wiki_title = f"{title} Wiki"
            wiki_summary = f"A wiki for {title}."
            # Create the new wiki and set it for the story.
            new_wiki_id = await self.create_wiki(user_id, wiki_title, wiki_summary)
            try:
                await self.client.set_story_wiki(story_id, new_wiki_id)
            except ClientError:
                raise FailedUpdateError(query='delete_wiki')
        # Recursively delete all segments in the wiki.
        segment_id = wiki['segment_id']
        deleted_link_ids = await self.delete_segment(segment_id)
        # Delete the wiki proper.
        try:
            await self.client.delete_wiki(wiki_id)
        except ClientError:
            raise FailedUpdateError(query='delete_wiki')
        else:
            return deleted_link_ids

    async def delete_segment(self, segment_id):
        deleted_link_ids = await self.recur_delete_segment_and_subsegments(segment_id)
        return deleted_link_ids

    async def recur_delete_segment_and_subsegments(self, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='recur_delete_segment_and_subsegments', value=segment_id)
        deleted_link_ids = []
        for subsegment_id in segment['segments']:
            segment_deleted_link_ids = await self.recur_delete_segment_and_subsegments(subsegment_id)
            deleted_link_ids.extend(segment_deleted_link_ids)
        for page_id in segment['pages']:
            page_deleted_link_ids = await self.delete_page(page_id)
            deleted_link_ids.extend(page_deleted_link_ids)
        try:
            await self.client.delete_segment(segment_id)
        except ClientError:
            raise FailedUpdateError(query='recur_delete_segment_and_subsegments')
        else:
            return deleted_link_ids

    async def delete_template_heading(self, title, segment_id):
        try:
            await self.client.delete_template_heading(title, segment_id)
        except ClientError:
            raise BadValueError(query='delete_template_heading', value=title)

    async def delete_page(self, page_id):
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='delete_page', value=page_id)
        deleted_link_ids = []
        for alias_id in page['aliases'].values():
            page_deleted_link_ids = await self._delete_alias_no_replace(alias_id)
            deleted_link_ids.extend(page_deleted_link_ids)
        try:
            await self.client.delete_page(page_id)
        except ClientError:
            raise FailedUpdateError(query='delete_page')
        else:
            return deleted_link_ids

    async def delete_heading(self, heading_title: str, page_id: ObjectId):
        try:
            await self.client.delete_heading(heading_title, page_id)
        except ClientError:
            raise FailedUpdateError(query='delete_heading')

    async def move_segment(self, segment_id, to_parent_id, to_index):
        if await self._segment_is_ancestor_of_candidate(segment_id, to_parent_id):
            raise BadValueError(query='move_segment', value=to_parent_id)
        try:
            await self.client.remove_segment_from_parent(segment_id)
        except ClientError:
            raise FailedUpdateError(query='move_segment')
        try:
            await self.client.insert_segment_to_parent_segment(segment_id, to_parent_id, to_index)
        except ClientError:
            raise FailedUpdateError(query='move_segment')

    async def _segment_is_ancestor_of_candidate(self, segment_id, candidate_segment_id):
        if segment_id == candidate_segment_id:
            return True
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='_segment_is_ancestor_of_candidate', value=segment_id)
        for subsegment_id in segment['segments']:
            if await self._segment_is_ancestor_of_candidate(subsegment_id, candidate_segment_id):
                return True
        return False

    async def move_page(self, page_id, to_parent_id, to_index):
        try:
            await self.client.remove_page_from_parent(page_id)
        except ClientError:
            raise FailedUpdateError(query='move_page')
        try:
            await self.client.insert_page_to_parent_segment(page_id, to_parent_id, to_index)
        except ClientError:
            raise FailedUpdateError(query='move_page')

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    async def create_link(self, story_id: ObjectId, section_id: ObjectId, paragraph_id: ObjectId, name: str,
                          page_id: ObjectId):
        # Check if alias exists.
        try:
            alias_id = await self.client.find_alias_in_page(page_id, name)
        except ClientError:
            # Create a new alias and add it to the page.
            alias_id = await self._create_alias(page_id, name)
        # Now create a link with the alias.
        link_id = await self.client.create_link(alias_id, page_id, story_id, section_id, paragraph_id)
        try:
            await self.client.insert_link_to_alias(link_id, alias_id)
        except ClientError:
            raise FailedUpdateError(query='create_link')
        try:
            # Insert the reference into the appropriate page.
            await self.client.insert_reference_to_page(page_id, link_id, story_id, section_id, paragraph_id)
        except ClientError:
            raise FailedUpdateError(query='create_link')
        else:
            return link_id

    async def get_link(self, link_id):
        try:
            link = await self.client.get_link(link_id)
        except ClientError:
            raise BadValueError(query='get_link', value=link_id)
        else:
            return link

    async def delete_link(self, link_id):
        link = await self.get_link(link_id)
        alias_id = link['alias_id']
        page_id = link['page_id']
        try:
            await self.client.remove_link_from_alias(link_id, alias_id)
        except ClientError:
            raise FailedUpdateError(query='delete_link')
        try:
            await self.client.remove_reference_from_page(link_id, page_id)
        except ClientError:
            raise FailedUpdateError(query='delete_link')
        try:
            await self.client.delete_link(link_id)
        except ClientError:
            raise FailedUpdateError(query='delete_link')

    async def comprehensive_remove_link(self, link_id: ObjectId, replacement_text: str):
        link = await self.get_link(link_id)
        context = link['context']
        try:
            text = await self.client.get_paragraph_text(context['section_id'], context['paragraph_id'])
        except ClientError:
            raise BadValueError(query='comprehensive_remove_link', value=link_id)
        # Strip spaces to handle the front-end's poor life choices regarding link IDs.
        serialized_link = encode_bson_to_string(link_id).replace(' ', '')
        updated_text = text.replace(serialized_link, replacement_text)
        # TOD: Come back to this.
        await self.set_paragraph_text(context['section_id'], updated_text, context['paragraph_id'])
        await self.delete_link(link_id)

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    async def change_alias_name(self, alias_id: ObjectId, new_name: str):
        # Update name in alias.
        try:
            alias = await self.client.get_alias(alias_id)
        except ClientError:
            raise BadValueError(query='change_alias_name', value=alias_id)
        page_id = alias['page_id']
        old_name = alias['name']
        try:
            await self.client.set_alias_name(new_name, alias_id)
        except ClientError:
            raise FailedUpdateError(query='change_alias_name')
        # Update `aliases` in the appropriate page.
        try:
            await self.client.update_alias_name_in_page(page_id, old_name, new_name)
        except ClientError:
            raise FailedUpdateError(query='change_alias_name')
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='change_alias_name', value=page_id)
        # Alias with page title renamed, need to recreate primary alias
        if not await self._page_title_is_alias(page):
            await self._create_alias(page_id, old_name)

    async def get_alias(self, alias_id: ObjectId):
        try:
            alias = await self.client.get_alias(alias_id)
        except ClientError:
            raise BadValueError(query='get_alias', value=alias_id)
        else:
            return alias

    async def delete_alias(self, alias_id: ObjectId):
        alias = await self.get_alias(alias_id)
        deleted_link_ids = await self._delete_alias_no_replace(alias_id)
        alias_name = alias['name']
        page_id = alias['page_id']
        try:
            page = await self.client.get_page(page_id)
        except ClientError:
            raise BadValueError(query='delete_alias', value=page_id)
        # Alias with page title deleted, need to recreate primary alias
        if page is not None and not await self._page_title_is_alias(page):
            await self._create_alias(page_id, alias_name)
        return deleted_link_ids

    async def _delete_alias_no_replace(self, alias_id: ObjectId):
        alias = await self.get_alias(alias_id)
        alias_name = alias['name']
        for link_id in alias['links']:
            await self.comprehensive_remove_link(link_id, alias_name)
        page_id = alias['page_id']
        try:
            await self.client.remove_alias_from_page(alias_name, page_id)
        except ClientError:
            raise FailedUpdateError(query='_delete_alias_no_replace')
        try:
            await self.client.delete_alias(alias_id)
        except ClientError:
            raise FailedUpdateError(query='_delete_alias_no_replace')
        else:
            return alias['links']

    async def _create_alias(self, page_id: ObjectId, name: str):
        alias_id = await self.client.create_alias(name, page_id)
        try:
            await self.client.insert_alias_to_page(page_id, name, alias_id)
        except ClientError:
            raise FailedUpdateError(query='_create_alias')
        else:
            return alias_id

    @staticmethod
    async def _page_title_is_alias(page):
        title = page['title']
        return page['aliases'].get(title) is not None

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    async def get_story_statistics(self, story_id):
        try:
            story = await self.client.get_story(story_id)
        except ClientError:
            raise BadValueError(query='get_story_statistics', value=story_id)
        stats = await self._recur_get_section_statistics(story['section_id'])
        return stats

    async def _recur_get_section_statistics(self, section_id):
        try:
            section = await self.client.get_section(section_id)
        except ClientError:
            raise BadValueError(query='_recur_get_section_statistics', value=section_id)
        word_freqs = Counter(section['statistics']['word_frequency'])
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            subsection_stats = await self._recur_get_section_statistics(subsection_id)
            word_freqs.update(subsection_stats['word_frequency'])
            section['statistics']['word_frequency'] = word_freqs
            section['statistics']['word_count'] += subsection_stats['word_count']
        return section['statistics']

    async def get_section_statistics(self, section_id):
        return await self._recur_get_section_statistics(section_id)

    async def get_paragraph_statistics(self, section_id, paragraph_id):
        try:
            stats = await self.client.get_paragraph_statistics(section_id, paragraph_id)
        except ClientError:
            raise BadValueError(query='get_paragraph_statistics', value=paragraph_id)
        else:
            return stats

    async def get_page_frequencies_in_story(self, story_id, wiki_id):
        try:
            wiki = await self.client.get_wiki(wiki_id)
        except ClientError:
            raise BadValueError(query='get_page_frequencies_in_story', value=wiki_id)
        segment_id = wiki['segment_id']
        return await self._get_page_section_frequencies(story_id, segment_id)

    async def _get_page_section_frequencies(self, story_id, segment_id):
        try:
            segment = await self.client.get_segment(segment_id)
        except ClientError:
            raise BadValueError(query='_get_page_section_frequencies', value=segment_id)
        pages = []
        for page_id in segment['pages']:
            try:
                page = await self.get_page(page_id)
            except ClientError:
                raise BadValueError(query='_get_page_section_frequencies', value=page_id)
            frequencies = defaultdict(int)
            for reference in filter(lambda ref: ref['story_id'] == story_id, page['references']):
                key = encode_bson_to_string(reference['section_id'])
                frequencies[key] += 1
            pages.append({'page_id': page_id, 'section_frequencies': frequencies})
        for child_segment_id in segment['segments']:
            child_pages = await self._get_page_section_frequencies(story_id, child_segment_id)
            pages.extend(child_pages)
        return pages


class MongoDBTornadoInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorTornadoClient, db_name, db_host, db_port, db_user, db_pass)


class MongoDBAsyncioInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorAsyncioClient, db_name, db_host, db_port, db_user, db_pass)
