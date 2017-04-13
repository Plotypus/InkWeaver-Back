from loom.loggers import db_queries_log, LogLevel

from bson.objectid import ObjectId
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection
from pymongo.results import DeleteResult, UpdateResult
from tornado.escape import url_escape
from typing import Any, Dict, List


class ClientError(Exception):
    pass


class BadMatchError(ClientError):
    pass


class NoMatchError(BadMatchError):
    pass


class ExtraMatchesError(BadMatchError):
    pass


class BadUpdateError(ClientError):
    pass


class NoUpdateError(BadUpdateError):
    pass


class ExtraUpdatesError(BadUpdateError):
    pass


class MongoDBClient:
    logger = db_queries_log

    def __init__(self, mongodb_client_class, db_name='inkweaver', db_host='localhost', db_port=27017, db_user=None,
                 db_pass=None):
        if db_user and db_pass:
            uri = 'mongodb://{username}:{password}@{hostname}:{port}/{db}'.format(
                username=url_escape(db_user),
                password=url_escape(db_pass),
                hostname=url_escape(db_host),
                port=db_port,
                db=url_escape(db_name)
            )
            self._client = mongodb_client_class(uri)
        else:
            self._client = mongodb_client_class(db_host, db_port)
        self._host = db_host
        self._port = db_port
        self._database = getattr(self._client, db_name)
        # Attempt to do something in the database to ensure connection was successful.
        self.database.collection_names()
        self.log("connected")

    def __repr__(self):
        return f'<{type(self)}|{self.host}:{self.port}>'

    def log(self, message, log_level=LogLevel.DEBUG):
        if isinstance(log_level, LogLevel):
            log_level = log_level
        self.logger.log(log_level, f'{repr(self)} {message}')

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    @property
    def client(self) -> AgnosticClient:
        return self._client

    @property
    def database(self) -> AgnosticDatabase:
        return self._database

    @property
    def collections(self) -> List[AgnosticCollection]:
        return [
            self.users,
            self.stories,
            self.sections,
            self.wikis,
            self.segments,
            self.pages,
            self.links,
            self.passive_links,
            self.aliases,
        ]

    @property
    def users(self) -> AgnosticCollection:
        return self.database.users

    @property
    def stories(self) -> AgnosticCollection:
        return self.database.stories

    @property
    def sections(self) -> AgnosticCollection:
        return self.database.sections

    @property
    def wikis(self) -> AgnosticCollection:
        return self.database.wikis

    @property
    def segments(self) -> AgnosticCollection:
        return self.database.segments

    @property
    def pages(self) -> AgnosticCollection:
        return self.database.pages

    @property
    def links(self) -> AgnosticCollection:
        return self.database.links

    @property
    def passive_links(self) -> AgnosticCollection:
        return self.database.passive_links

    @property
    def aliases(self) -> AgnosticCollection:
        return self.database.aliases

    async def authenticate(self, username, password):
        await self.database.authenticate(username, password)

    async def drop_database(self):
        await self.client.drop_database(self.database)

    @staticmethod
    async def drop_collection(collection: AgnosticCollection):
        await collection.drop()

    async def drop_all_collections(self):
        [await self.drop_collection(collection) for collection in self.collections]

    @staticmethod
    def assert_update_was_successful(update_result: UpdateResult):
        if update_result.matched_count == 0:
            raise NoMatchError                  # pragma: no cover

    @staticmethod
    def assert_delete_one_successful(delete_result: DeleteResult):
        if delete_result.deleted_count == 0:
            raise NoMatchError                  # pragma: no cover

    @staticmethod
    def update_dict_if_value_is_not_none(dictionary: Dict, field: str, value: Any):
        if value is not None:
            dictionary[field] = value

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    async def create_user(self,
                          username: str,
                          password_hash: str,
                          name: str,
                          email: str,
                          bio: str,
                          avatar=None,
                          _id=None) -> ObjectId:
        user = {
            'username':      username,
            'password_hash': password_hash,
            'name':          name,
            'email':         email,
            'bio':           bio,
            'avatar':        avatar,
            'stories':       list(),
            'wikis':         list(),
            'statistics':    None,
        }
        if _id is not None:
            user['_id'] = _id
        result = await self.users.insert_one(user)
        self.log(f'create_user {{{username}}}; inserted ID: {{{result.inserted_id}}}')
        return result.inserted_id

    async def get_user_for_user_id(self, user_id: ObjectId):
        user = await self.users.find_one(
            filter={'_id': user_id}
        )
        if user is None:
            self.log(f'get_user_for_user_id {{{user_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_user_for_user_id {{{user_id}}}')
        return user

    async def get_password_hash_for_username(self, username: str) -> str:
        user = await self.users.find_one(
            filter={'username': username},
            projection={
                'password_hash': 1,
            }
        )
        if user is None:
            self.log(f'get_password_hash_for_username {{{username}}} FAILED')
            raise NoMatchError
        self.log(f'get_password_hash_for_username {{{username}}}', LogLevel.DEBUG)
        return user['password_hash']

    async def get_user_id_for_username(self, username: str) -> ObjectId:
        user = await self.users.find_one(
            filter={'username': username},
            projection={
                '_id': 1,
            }
        )
        if user is None:
            self.log(f'get_user_id_for_username {{{username}}} FAILED')
            raise NoMatchError
        user_id = user['_id']
        self.log(f'get_user_id_for_username {{{username}}}; user ID {{{user_id}}}')
        return user_id

    async def get_user_for_username(self, username: str):
        user = await self.users.find_one(
            filter={'username': username}
        )
        if user is None:
            self.log(f'get_user_for_username {{{username}}} FAILED')
            raise NoMatchError
        self.log(f'get_user_for_username {{{username}}}')
        return user

    async def username_exists(self, username: str) -> bool:
        user = await self.users.find_one(
            filter={'username': username}
        )
        self.log(f'username_exists {{{username}}}')
        return user is not None

    async def email_exists(self, email: str) -> bool:
        user = await self.users.find_one(
            filter={'email': email}
        )
        self.log(f'email_exists {{{email}}}')
        return user is not None

    async def add_story_to_user(self, user_id: ObjectId, story_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$push': {
                    'stories': {
                        'story_id': story_id,
                        'position_context': None,
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'add_story_to_user {{{story_id}}} for user {{{user_id}}}')

    async def add_wiki_to_user(self, user_id: ObjectId, wiki_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$push': {
                    'wikis': wiki_id
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'add_wiki_to_user {{{wiki_id}}} for user {{{user_id}}}')

    async def set_user_password_hash(self, user_id, password_hash):
        return await self.set_user_field(user_id, 'password_hash', password_hash)

    async def set_user_name(self, user_id, name):
        return await self.set_user_field(user_id, 'name', name)

    async def set_user_email(self, user_id, email):
        return await self.set_user_field(user_id, 'email', email)

    async def set_user_bio(self, user_id, bio):
        return await self.set_user_field(user_id, 'bio', bio)

    async def set_user_avatar(self, user_id, avatar):
        return await self.set_user_field(user_id, 'avatar', avatar)

    async def set_user_field(self, user_id, field, value):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$set': {
                    field: value
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_user_field {{{field}}} for user {{{user_id}}}')

    async def set_user_story_position_context(self, user_id, story_id, position_context):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id, 'stories.story_id': story_id},
            update={
                '$set': {
                    'stories.$.position_context': position_context,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_user_story_position_context for user {{{user_id}}} for story {{{story_id}}}')

    async def get_user_preferences(self, user_id: ObjectId) -> Dict:
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':      0,
                'username': 1,
                'name':     1,
                'email':    1,
                'bio':      1,
                'avatar':   1,
            }
        )
        if result is None:
            self.log(f'get_user_preferences for user {{{user_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_user_preferences for user {{{user_id}}}')
        return result

    async def get_user_stories(self, user_id: ObjectId) -> List[Dict]:
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':     0,
                'stories': 1,
            }
        )
        if result is None:
            self.log(f'get_user_stories for user {{{user_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_user_stories for user {{{user_id}}}')
        return result['stories']

    async def get_user_wiki_ids(self, user_id: ObjectId) -> List[ObjectId]:
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':   0,
                'wikis': 1,
            }
        )
        if result is None:
            self.log(f'get_user_wiki_ids for user {{{user_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_user_wiki_ids for user {{{user_id}}}')
        return result['wikis']

    async def remove_story_from_user(self, user_id: ObjectId, story_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$pull': {
                    'stories': {
                        'story_id': story_id
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_story_from_user for user {{{user_id}}} for story {{{story_id}}}')

    async def remove_wiki_from_user(self, user_id: ObjectId, wiki_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$pull': wiki_id
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_wiki_from_user for user {{{user_id}}} for wiki {{{wiki_id}}}')

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    async def create_story(self,
                           title: str,
                           wiki_id: ObjectId,
                           user_description,
                           section_id: ObjectId,
                           _id=None) -> ObjectId:
        story = {
            'title':      title,
            'wiki_id':    wiki_id,
            'users':      [user_description],
            'section_id': section_id,
            'bookmarks':  list(),
            'statistics': None,
            'settings':   None,
        }
        if _id is not None:
            story['_id'] = _id
        result = await self.stories.insert_one(story)
        self.log(f'create_story {{{title}}} attached to wiki {{{wiki_id}}} with head section {{{section_id}}}; '
                 f'inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def create_section(self, title: str, _id=None) -> ObjectId:
        section = {
            'title':                  title,
            'content':                list(),  # content is a list of "paragraph objects"
            'preceding_subsections':  list(),
            'inner_subsections':      list(),
            'succeeding_subsections': list(),
            'statistics':             {'word_frequency': {}, 'word_count': 0},
            'links':                  list(),  # links is a list of lists of links (runs parallel to paragraphs)
            'passive_links':          list(),
            'notes':                  list(),
        }
        if _id is not None:
            section['_id'] = _id
        result = await self.sections.insert_one(section)
        self.log(f'create_section {{{title}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    @staticmethod
    def _insertion_parameters(obj, position=None):
        inner_parameters = {
            '$each': [obj],
        }
        if position is not None:
            inner_parameters['$position'] = position
        return inner_parameters

    async def insert_user_description_to_story(self, user_description: dict, story_id: ObjectId, at_index=None):
        inner_parameters = self._insertion_parameters(user_description, at_index)
        update_result: UpdateResult = await self.stories.update_one(
            filter={'_id': story_id},
            update={
                '$push': {
                    'users': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_user_description_to_story {{{user_description}}} to story {{{story_id}}} at index '
                 f'{{{at_index}}}')

    async def insert_preceding_subsection(self, subsection_id, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters(subsection_id, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'preceding_subsections': inner_parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_preceding_subsection {{{subsection_id}}} to section {{{to_section_id}}} at index '
                 f'{{{at_index}}}')

    async def insert_inner_subsection(self, subsection_id, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters(subsection_id, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'inner_subsections': inner_parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_inner_subsection {{{subsection_id}}} to section {{{to_section_id}}} at index {{{at_index}}}')

    async def insert_succeeding_subsection(self, subsection_id, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters(subsection_id, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'succeeding_subsections': inner_parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_succeeding_subsection {{{subsection_id}}} to section {{{to_section_id}}} at index '
                 f'{{{at_index}}}')

    async def insert_paragraph(self, paragraph_id: ObjectId, text: str, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters({
            '_id':        paragraph_id,
            'text':       text,
            'statistics': {'word_frequency': {}, 'word_count': 0},
        }, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'content': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_paragraph {{{paragraph_id}}} to section {{{to_section_id}}} at index {{{at_index}}}')

    async def insert_note_for_paragraph(self, paragraph_id: ObjectId, in_section_id, note=None, at_index=None):
        inner_parameters = self._insertion_parameters({
            'paragraph_id': paragraph_id,
            'note': note,
        }, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': in_section_id},
            update={
                '$push': {
                    'notes': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_note_for_paragraph {{{paragraph_id}}} in section {{{in_section_id}}} at index {{{at_index}}}')

    async def insert_bookmark(self, bookmark_id: ObjectId, story_id: ObjectId, section_id: ObjectId,
                              paragraph_id: ObjectId, name: str, at_index=None):
        inner_parameters = self._insertion_parameters({
            'bookmark_id': bookmark_id,
            'section_id': section_id,
            'paragraph_id': paragraph_id,
            'name': name,
        }, at_index)
        update_result: UpdateResult = await self.stories.update_one(
            filter={'_id': story_id},
            update={
                '$push': {
                    'bookmarks': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_bookmark {{{bookmark_id}}} for story {{{story_id}}}')

    async def set_story_wiki(self, story_id: ObjectId, wiki_id: ObjectId):
        update_result: UpdateResult = await self.stories.update_one(
            filter={'_id': story_id},
            update={
                '$set': {
                    'wiki_id': wiki_id
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_story_wiki {{{story_id}}} to wiki {{{wiki_id}}}')

    async def set_story_title(self, story_id: ObjectId, new_title: str):
        update_result: UpdateResult = await self.stories.update_one(
            filter={'_id': story_id},
            update={
                '$set': {
                    'title': new_title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_story_title {{{story_id}}} to title {{{new_title}}}')

    async def set_section_title(self, section_id: ObjectId, title: str):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id},
            update={
                '$set': {
                    'title': title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_section_title {{{section_id}}} to title {{{title}}}')

    async def set_section_statistics(self, section_id: ObjectId, wf_table: dict, word_count: int):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id},
            update={
                '$set': {
                    'statistics.word_frequency': wf_table,
                    'statistics.word_count': word_count
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_section_statistics {{{section_id}}}')

    async def set_paragraph_text(self, paragraph_id: ObjectId, text: str, in_section_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_one(
            # For filtering documents in an array, we use the name of the array field
            # combined with the field in the document we want to filter with. In this case,
            # we want to filter for the `_id` in the `content` array.
            filter={'_id': in_section_id, 'content._id': paragraph_id},
            update={
                '$set': {
                    # The `$` acts as a placeholder to update the first element that
                    # matches the query condition.
                    'content.$.text': text
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_paragraph_text {{{paragraph_id}}} in section {{{in_section_id}}}')

    async def set_paragraph_statistics(self, paragraph_id: ObjectId, wf_table: dict, word_count: int,
                                       in_section_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': in_section_id, 'content._id': paragraph_id},
            update={
                '$set': {
                    'content.$.statistics.word_frequency': wf_table,
                    'content.$.statistics.word_count': word_count
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_paragraph_statistics {{{paragraph_id}}} in section {{{in_section_id}}}')

    async def set_bookmark_name(self, story_id: ObjectId, bookmark_id: ObjectId, new_name: str):
        update_result: UpdateResult = await self.stories.update_one(
            filter={'_id': story_id, 'bookmarks.bookmark_id': bookmark_id},
            update={
                '$set': {
                    'bookmarks.$.name': new_name
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_bookmark_name {{{bookmark_id}}} in story {{{story_id}}} to {{{new_name}}}')

    async def set_note(self, section_id: ObjectId, paragraph_id: ObjectId, text: str):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id, 'notes.paragraph_id': paragraph_id},
            update={
                '$set': {
                    'notes.$.note': text
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_note for paragraph {{{paragraph_id}}} in section {{{section_id}}}')

    async def get_story(self, story_id: ObjectId) -> Dict:
        result = await self.stories.find_one({'_id': story_id})
        if result is None:
            self.log(f'get_story {{{story_id}}}  FAILED')
            raise NoMatchError
        self.log(f'get_story {{{story_id}}}')
        return result

    async def get_section(self, section_id: ObjectId) -> Dict:
        result = await self.sections.find_one({'_id': section_id})
        if result is None:
            self.log(f'get_section {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_section {{{section_id}}}')
        return result

    async def get_section_statistics(self, section_id: ObjectId):
        projected_section = await self.sections.find_one(
            filter={'_id': section_id},
            projection={
                'statistics': 1,
                '_id': 0,
            }
        )
        if projected_section is None:
            self.log(f'get_section_statistics {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_section_statistics {{{section_id}}}')
        return projected_section['statistics']

    async def get_paragraph_ids(self, section_id: ObjectId):
        pipeline = [{'$unwind': '$content'}, {'$match': {'_id': section_id}},
                    {'$project': {'content._id': 1, '_id': 0}}]
        results = []
        async for doc in self.sections.aggregate(pipeline):
            if doc is None:
                self.log(f'get_paragraph_ids {{{section_id}}} FAILED')
                raise NoMatchError
            results.append(doc['content']['_id'])
        self.log(f'get_paragraph_ids for section {{{section_id}}}')
        return results

    async def get_paragraph_text(self, section_id: ObjectId, paragraph_id: ObjectId):
        projected_section = await self.sections.find_one(
            filter={'_id': section_id, 'content._id': paragraph_id},
            projection={
                'content.$.text': 1,
                '_id': 0,
            }
        )
        if projected_section is None:
            self.log(f'get_paragraph_text {{{paragraph_id}}} in section {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_paragraph_text {{{paragraph_id}}} in section {{{section_id}}}')
        return projected_section['content'][0]['text']

    async def get_paragraph_statistics(self, section_id: ObjectId, paragraph_id: ObjectId):
        projected_section = await self.sections.find_one(
            filter={'_id': section_id, 'content._id': paragraph_id},
            projection={
                'content.$.statistics': 1,
                '_id': 0,
            }
        )
        if projected_section is None:
            self.log(f'get_paragraph_statistics {{{paragraph_id}}} in section {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_paragraph_statistics {{{paragraph_id}}} in section {{{section_id}}}')
        return projected_section['content'][0]['statistics']

    async def delete_story(self, story_id: ObjectId):
        delete_result: DeleteResult = await self.stories.delete_one(
            filter={'_id': story_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_story {{{story_id}}}')

    async def remove_section_from_parent(self, section_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_many(
            filter={},
            update={
                '$pull': {
                    'preceding_subsections':  section_id,
                    'inner_subsections':      section_id,
                    'succeeding_subsections': section_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_section_from_parent {{{section_id}}}')

    async def delete_section(self, section_id: ObjectId):
        await self.remove_section_from_parent(section_id)
        delete_result: DeleteResult = await self.sections.delete_one(
            filter={'_id': section_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_section {{{section_id}}}')

    async def delete_paragraph(self, section_id: ObjectId, paragraph_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id},
            update={
                '$pull': {
                    'content': {
                        '_id': paragraph_id,
                    },
                    'links': {
                        'paragraph_id': paragraph_id,
                    },
                    'passive_links': {
                        'paragraph_id': paragraph_id,
                    },
                    'notes': {
                        'paragraph_id': paragraph_id,
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_paragraph {{{paragraph_id}}} in section {{{section_id}}}')

    async def delete_bookmark_by_id(self, bookmark_id: ObjectId):
        update_result: UpdateResult = await self.stories.update_many(
            filter={},
            update={
                '$pull': {
                    'bookmarks': {
                        'bookmark_id': bookmark_id
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_bookmark_by_id {{{bookmark_id}}}')

    async def delete_bookmark_by_section_id(self, section_id: ObjectId):
        update_result: UpdateResult = await self.stories.update_many(
            filter={},
            update={
                '$pull': {
                    'bookmarks': {
                        'section_id': section_id
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_bookmark_by_section_id {{{section_id}}}')

    async def delete_bookmark_by_paragraph_id(self, paragraph_id: ObjectId):
        update_result: UpdateResult = await self.stories.update_many(
            filter={},
            update={
                '$pull': {
                    'bookmarks': {
                        'paragraph_id': paragraph_id
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_bookmark_by_paragraph_id {{{paragraph_id}}}')

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, title: str, user_description, summary: str, segment_id: ObjectId, _id=None) -> ObjectId:
        wiki = {
            'title':      title,
            'users':      [user_description],
            'summary':    summary,
            'segment_id': segment_id,
            'statistics': None,
            'settings':   None,
        }
        if _id is not None:
            wiki['_id'] = _id
        result = await self.wikis.insert_one(wiki)
        self.log(f'create_wiki {{{title}}} with head segment {{{segment_id}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def create_segment(self, title: str, template_headings=None, _id=None) -> ObjectId:
        segment = {
            'title':             title,
            'segments':          list(),
            'pages':             list(),
            'template_headings': list(),
            'statistics':        None,
        }
        if template_headings is not None:
            segment['template_headings'] = template_headings
        if _id is not None:
            segment['_id'] = _id
        result = await self.segments.insert_one(segment)
        self.log(f'create_segment {{{title}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def create_page(self, title: str, template_headings=None, _id=None) -> ObjectId:
        page = {
            'title':      title,
            'headings':   list() if template_headings is None else template_headings,
            'references': list(),  # list[Reference] (see Loom's wiki for more detail)
            'aliases':    dict(),
        }
        if _id is not None:
            page['_id'] = _id
        result = await self.pages.insert_one(page)
        self.log(f'create_page {{{title}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def insert_user_description_to_wiki(self, user_description: dict, wiki_id: ObjectId, at_index=None):
        inner_parameters = self._insertion_parameters(user_description, at_index)
        update_result: UpdateResult = await self.wikis.update_one(
            filter={'_id': wiki_id},
            update={
                '$push': {
                    'users': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_user_description_to_wiki {{{user_description}}} to wiki {{{wiki_id}}} at index '
                 f'{{{at_index}}}')

    async def insert_segment_to_parent_segment(self, child_segment: ObjectId, parent_segment: ObjectId, at_index=None):
        inner_parameters = self._insertion_parameters(child_segment, at_index)
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': parent_segment},
            update={
                '$push': {
                    'segments': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'append_segment_to_parent_segment {{{child_segment}}} to parent {{{parent_segment}}}')

    async def insert_page_to_parent_segment(self, page_id: ObjectId, segment_id: ObjectId, at_index=None):
        inner_parameters = self._insertion_parameters(page_id, at_index)
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$push': {
                    'pages': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'append_page_to_parent_segment {{{page_id}}} to parent {{{segment_id}}}')

    async def insert_template_heading_to_segment(self, title: str, segment_id: ObjectId, text='', at_index=None):
        template_heading = {
            'title': title,
            'text':  text,
        }
        inner_parameters = self._insertion_parameters(template_heading, at_index)
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$push': {
                    'template_headings': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'append_template_heading_to_segment {{{title}}} to segment {{{segment_id}}}')

    async def insert_heading(self, title: str, page_id: ObjectId, text='', at_index=None):
        heading = {
            'title': title,
            'text':  text,
        }
        inner_parameters = self._insertion_parameters(heading, at_index)
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$push': {
                    'headings': inner_parameters
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_heading {{{title}}} to page {{{page_id}}} at index {{{at_index}}}')

    async def set_wiki_title(self, new_title: str, wiki_id: ObjectId):
        update_result: UpdateResult = await self.wikis.update_one(
            filter={'_id': wiki_id},
            update={
                '$set': {
                    'title': new_title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_wiki_title {{{wiki_id}}} to title {{{new_title}}}')

    async def set_segment_title(self, title: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$set': {
                    'title': title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_segment_title {{{segment_id}}} to title {{{title}}}')

    async def set_template_heading_title(self, old_title: str, new_title: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id, 'template_headings.title': old_title},
            update={
                '$set': {
                    'template_headings.$.title': new_title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_template_heading_title from {{{old_title}}} to {{{new_title}}} in segment {{{segment_id}}}')

    async def set_template_heading_text(self, title: str, text: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id, 'template_headings.title': title},
            update={
                '$set': {
                    'template_headings.$.text': text
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_template_heading_text for heading {{{title}}} in segment {{{segment_id}}}')

    async def set_page_title(self, new_title: str, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$set': {
                    'title': new_title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_page_title {{{page_id}}} to title {{{new_title}}}')

    async def set_heading_title(self, old_title: str, new_title: str, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            # For filtering documents in an array, we use the name of the array field
            # combined with the field in the document we want to filter with. In this case,
            # we want to filter for the `title` in the `headings` array.
            filter={'_id': page_id, 'headings.title': old_title},
            update={
                '$set': {
                    # The `$` acts as a placeholder to update the first element that
                    # matches the query condition. In this case, the first document
                    # with the old title.
                    'headings.$.title': new_title
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_heading_title from {{{old_title}}} to {{{new_title}}} in page {{{page_id}}}')

    async def set_heading_text(self, title: str, text: str, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            # For filtering documents in an array, we use the name of the array field
            # combined with the field in the document we want to filter with. In this case,
            # we want to filter for the `title` in the `headings` array.
            filter={'_id': page_id, 'headings.title': title},
            update={
                '$set': {
                    # The `$` acts as a placeholder to update the first element that
                    # matches the query condition. In this case, the first document
                    # with the old title.
                    'headings.$.text': text
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_heading_text for heading {{{title}}} in page {{{page_id}}}')

    async def set_page_references(self, page_id: ObjectId, references: List):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$set': {
                    'references': references,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_page_references {{{page_id}}}')

    async def get_wiki(self, wiki_id: ObjectId) -> Dict:
        result = await self.wikis.find_one({'_id': wiki_id})
        if result is None:
            self.log(f'get_wiki {{{wiki_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_wiki {{{wiki_id}}}')
        return result

    async def get_segment(self, segment_id: ObjectId) -> Dict:
        result = await self.segments.find_one({'_id': segment_id})
        if result is None:
            self.log(f'get_segment {{{segment_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_segment {{{segment_id}}}')
        return result

    async def get_page(self, page_id: ObjectId) -> Dict:
        result = await self.pages.find_one({'_id': page_id})
        if result is None:
            self.log(f'get_page {{{page_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_page {{{page_id}}}')
        return result

    async def get_template_heading(self, title: str, segment_id: ObjectId):
        result = await self.segments.find_one({
            '_id':                     segment_id,
            'template_headings.title': title
        })
        if result is None:
            self.log(f'get_template_heading {{{title}}} in segment {{{segment_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_template_heading {{{title}}} in segment {{{segment_id}}}')
        # The result we get back is for the segment, not the template heading.
        # So, we should iterate through to find it.
        for template_heading in result['template_headings']:
            if template_heading['title'] == title:
                return template_heading
        # This error is unreachable, because we already know the template heading exists.
        raise NoMatchError

    async def get_heading(self, title: str, page_id: ObjectId):
        result = await self.pages.find_one({
            '_id':            page_id,
            'headings.title': title
        })
        if result is None:
            self.log(f'get_heading {{{title}}} in page {{{page_id}}}')
            raise NoMatchError
        self.log(f'get_heading {{{title}}} in page {{{page_id}}}')
        # The result we get back is for the page, not the heading.
        # So, we should iterate through to find it.
        for heading in result['headings']:
            if heading['title'] == title:
                return heading
        # This error is unreachable, because we already know the heading exists.
        raise NoMatchError

    async def get_summaries_of_stories_using_wiki(self, wiki_id: ObjectId):
        result_cursor = self.stories.find(
            filter={'wiki_id': wiki_id},
            projection={'_id': 1, 'title': 1}
        )
        results = []
        async for result in result_cursor:
            if result is None:
                self.log(f'get_summaries_of_stories_using_wiki {{{wiki_id}}} FAILED')
                raise NoMatchError
            results.append(result)
        self.log(f'get_summaries_of_stories_using_wiki {{{wiki_id}}}')
        return results

    async def delete_wiki(self, wiki_id: ObjectId):
        parent_update_result: UpdateResult = await self.users.update_many(
            filter={},
            update={
                '$pull': {
                    'wikis': wiki_id
                }
            }
        )
        self.assert_update_was_successful(parent_update_result)
        delete_result: DeleteResult = await self.wikis.delete_one(
            filter={'_id': wiki_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_wiki {{{wiki_id}}}')

    async def delete_segment(self, segment_id: ObjectId):
        await self.remove_segment_from_parent(segment_id)
        delete_result: DeleteResult = await self.segments.delete_one(
            filter={'_id': segment_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_segment {{{segment_id}}}')

    async def remove_segment_from_parent(self, segment_id: ObjectId):
        parent_update_result: UpdateResult = await self.segments.update_many(
            filter={},
            update={
                '$pull': {
                    'segments': segment_id
                }
            }
        )
        self.assert_update_was_successful(parent_update_result)
        self.log(f'remove_segment_from_parent {{{segment_id}}}')

    async def delete_template_heading(self, template_heading_title: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$pull': {
                    'template_headings': {
                        'title': template_heading_title
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_template_heading {{{template_heading_title}}} in segment {{{segment_id}}}')

    async def delete_page(self, page_id: ObjectId):
        await self.remove_page_from_parent(page_id)
        delete_result: DeleteResult = await self.pages.delete_one(
            filter={'_id': page_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_page {{{page_id}}}')

    async def remove_page_from_parent(self, page_id: ObjectId):
        parent_update_result: UpdateResult = await self.segments.update_many(
            filter={},
            update={
                '$pull': {
                    'pages': page_id
                }
            }
        )
        self.assert_update_was_successful(parent_update_result)
        self.log(f'remove_page_from_parent {{{page_id}}}')

    async def delete_heading(self, heading_title, page_id):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$pull': {
                    'headings': {
                        'title': heading_title
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'delete_heading {{{heading_title}}} in page {{{page_id}}}')

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @staticmethod
    def _build_link_context(story_id, section_id, paragraph_id, text):
        context = {
            'story_id':     story_id,
            'section_id':   section_id,
            'paragraph_id': paragraph_id,
            'text':         text,
        }
        return context

    async def create_link(self, alias_id: ObjectId, page_id: ObjectId, story_id=None, section_id=None,
                          paragraph_id=None, text=None, _id=None) -> ObjectId:
        context = self._build_link_context(story_id, section_id, paragraph_id, text)
        link = {
            'context':  context,
            'alias_id': alias_id,
            'page_id':  page_id,
        }
        if _id is not None:
            link['_id'] = _id
        result = await self.links.insert_one(link)
        self.log(f'create_link to page {{{page_id}}} for alias {{{alias_id}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def get_link(self, link_id: ObjectId):
        result = await self.links.find_one({'_id': link_id})
        if result is None:
            self.log(f'get_link {{{link_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_link {{{link_id}}}')
        return result

    async def get_links_in_paragraph(self, paragraph_id: ObjectId, section_id: ObjectId):
        section_projection = await self.sections.find_one(
            filter={'_id': section_id, 'links.paragraph_id': paragraph_id},
            projection={'links.links': 1, '_id': 0}
        )
        if section_projection is None:
            self.log(f'get_links_in_paragraph {{{paragraph_id}}} in section {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_links_in_paragraph {{{paragraph_id}}} in section {{{section_id}}}')
        return section_projection['links'][0]['links']

    async def set_link_context(self, link_id: ObjectId, context: Dict):
        update_result: UpdateResult = await self.links.update_one(
            filter={'_id': link_id},
            update={
                '$set': {
                    'context': context,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_link_context {{{link_id}}}')

    async def update_link_context(self, link_id: ObjectId, paragraph_id: ObjectId, text: str, story_id=None,
                                  section_id=None):
        update_fields = {
            'context.paragraph_id': paragraph_id,
            'context.text':         text,
        }
        self.update_dict_if_value_is_not_none(update_fields, 'context.story_id', story_id)
        self.update_dict_if_value_is_not_none(update_fields, 'context.section_id', section_id)
        update_result: UpdateResult = await self.links.update_one(
            filter={'_id': link_id},
            update={
                '$set': update_fields,
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'update_link_context {{{link_id}}}')

    async def insert_reference_to_page(self, page_id: ObjectId, link_id: ObjectId, story_id: ObjectId,
                                       section_id: ObjectId, paragraph_id: ObjectId, text=None, index=None):
        context = self._build_link_context(story_id, section_id, paragraph_id, text)
        reference = {
            'link_id': link_id,
            'context': context,
        }
        parameters = self._insertion_parameters(reference, index)
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$push': {
                    'references': parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_reference_to_page {{{page_id}}} with link {{{link_id}}}')

    async def insert_links_for_paragraph(self, paragraph_id: ObjectId, links: List[ObjectId], in_section_id: ObjectId,
                                         at_index=None):
        inner_parameters = self._insertion_parameters({
            'paragraph_id': paragraph_id,
            'links':        links,
        }, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': in_section_id},
            update={
                '$push': {
                    'links': inner_parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_links_for_paragraph {{{paragraph_id}}} in section {{{in_section_id}}} at index '
                 f'{{{at_index}}}')

    async def set_links_in_section(self, section_id: ObjectId, links: List[ObjectId], paragraph_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id, 'links.paragraph_id': paragraph_id},
            update={
                '$set': {
                    'links.$.links': links,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_links_in_section {{{section_id}}}')

    async def remove_reference_from_page(self, link_id: ObjectId, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$pull': {
                    'references': {
                        'link_id': link_id,
                    }
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_reference_from_page {{{link_id}}} from page {{{page_id}}}')

    async def delete_link(self, link_id: ObjectId):
        delete_result: DeleteResult = await self.links.delete_one(
            filter={'_id': link_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_link {{{link_id}}}')

    ###########################################################################
    #
    # Passive Link Methods
    #
    ###########################################################################

    @staticmethod
    def _build_passive_link_context(section_id, paragraph_id):
        context = {
            'section_id':   section_id,
            'paragraph_id': paragraph_id,
        }
        return context

    async def create_passive_link(self, alias_id: ObjectId, page_id: ObjectId, section_id=None, paragraph_id=None,
                                  _id=None):
        context = self._build_passive_link_context(section_id, paragraph_id)
        passive_link = {
            'context':  context,
            'alias_id': alias_id,
            'page_id':  page_id,
            'pending':  True,
        }
        if _id is not None:
            passive_link['_id'] = _id
        result = await self.passive_links.insert_one(passive_link)
        self.log(f'create_passive_link to page {{{page_id}}} for alias {{{alias_id}}}; '
                 f'inserted ID {{{result.inserted_id}}}')
        return result.inserted_id
    
    async def get_passive_link(self, passive_link_id: ObjectId):
        result = await self.passive_links.find_one({'_id': passive_link_id})
        if result is None:
            self.log(f'get_passive_link {{{passive_link_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_passive_link {{{passive_link_id}}}')
        return result

    async def get_passive_links_in_paragraph(self, paragraph_id: ObjectId, section_id: ObjectId):
        section_projection = await self.sections.find_one(
            filter={'_id': section_id, 'passive_links.paragraph_id': paragraph_id},
            projection={'passive_links.passive_links': 1, '_id': 0}
        )
        if section_projection is None:
            self.log(f'get_passive_links_in_paragraph {{{paragraph_id}}} in section {{{section_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_passive_links_in_paragraph {{{paragraph_id}}} in section {{{section_id}}}')
        return section_projection['passive_links'][0]['passive_links']

    async def set_passive_link_context(self, passive_link_id: ObjectId, context: Dict):
        update_result: UpdateResult = await self.passive_links.update_one(
            filter={'_id': passive_link_id},
            update={
                '$set': {
                    'context': context,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_passive_link_context {{{passive_link_id}}}')

    async def reject_passive_link(self, passive_link_id: ObjectId):
        update_result: UpdateResult = await self.passive_links.update_one(
            filter={'_id': passive_link_id},
            update={
                '$set': {
                    'pending': False,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'reject_passive_link {{{passive_link_id}}}')

    async def insert_passive_links_for_paragraph(self, paragraph_id: ObjectId, passive_links: List[ObjectId],
                                                 in_section_id: ObjectId, at_index=None):
        inner_parameters = self._insertion_parameters({
            'paragraph_id': paragraph_id,
            'passive_links':        passive_links,
        }, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': in_section_id},
            update={
                '$push': {
                    'passive_links': inner_parameters,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_passive_links_for_paragraph {{{paragraph_id}}} in section {{{in_section_id}}} at index '
                 f'{{{at_index}}}')

    async def set_passive_links_in_section(self, section_id: ObjectId, passive_links: List[ObjectId],
                                           paragraph_id: ObjectId):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': section_id, 'passive_links.paragraph_id': paragraph_id},
            update={
                '$set': {
                    'passive_links.$.passive_links': passive_links,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_passive_links_in_section {{{section_id}}}')

    async def delete_passive_link(self, passive_link_id: ObjectId):
        delete_result: DeleteResult = await self.passive_links.delete_one(
            filter={'_id': passive_link_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_passive_link {{{passive_link_id}}}')

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    async def create_alias(self, name: str, page_id: ObjectId, _id=None) -> ObjectId:
        alias = {
            'name':          name,
            'page_id':       page_id,
            'links':         list(),
            'passive_links': list(),
        }
        if _id is not None:
            alias['_id'] = _id
        result = await self.aliases.insert_one(alias)
        self.log(f'create_alias {{{name}}} in page {{{page_id}}}; inserted ID {{{result.inserted_id}}}')
        return result.inserted_id

    async def set_alias_name(self, name: str, alias_id: ObjectId):
        update_result: UpdateResult = await self.aliases.update_one(
            filter={'_id': alias_id},
            update={
                '$set': {
                    'name': name
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'set_alias_name {{{alias_id}}} to name {{{name}}}')

    async def insert_link_to_alias(self, link_id: ObjectId, alias_id: ObjectId):
        update_result: UpdateResult = await self.aliases.update_one(
            filter={'_id': alias_id},
            update={
                '$push': {
                    'links': link_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_link_to_alias {{{link_id}}} to alias {{{alias_id}}}')

    async def insert_passive_link_to_alias(self, passive_link_id: ObjectId, alias_id: ObjectId):
        update_result: UpdateResult = await self.aliases.update_one(
            filter={'_id': alias_id},
            update={
                '$push': {
                    'passive_links': passive_link_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_passive_link_to_alias {{{passive_link_id}}} to alias {{{alias_id}}}')

    async def get_alias(self, alias_id: ObjectId):
        result = await self.aliases.find_one({'_id': alias_id})
        if result is None:
            self.log(f'get_alias FAILED')
            raise NoMatchError
        self.log(f'get_alias {{{alias_id}}}')
        return result

    async def insert_alias_to_page(self, page_id: ObjectId, name: str, alias_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$set': {
                    'aliases.{}'.format(name): alias_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'insert_alias_to_page {{{alias_id}}} to page {{{page_id}}}')

    async def update_alias_name_in_page(self, page_id: ObjectId, old_name: str, new_name: str):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$rename': {
                    'aliases.{}'.format(old_name): 'aliases.{}'.format(new_name),
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'update_alias_name_in_page {{{page_id}}} from {{{old_name}}} to {{{new_name}}}')

    async def get_aliases_from_page(self, page_id: ObjectId):
        result = await self.pages.find_one(
            filter={'_id': page_id},
            projection={'_id': 0, 'aliases': 1}
        )
        if result is None:
            self.log(f'get_aliases_from_page {{{page_id}}} FAILED')
            raise NoMatchError
        self.log(f'get_aliases_from_page {{{page_id}}}')
        return None if result is None else result['aliases']

    async def find_alias_in_page(self, page_id: ObjectId, name: str):
        alias_field = 'aliases.{}'.format(name)
        pipeline = [
            {'$match': {'_id': page_id, alias_field: {'$exists': True}}},
            {'$project': {alias_field: 1, '_id': 0}},
        ]
        results = []
        self.log(f'find_alias_in_page {{{page_id}}} with name {{{name}}}')
        async for match in self.pages.aggregate(pipeline):
            results.append(match['aliases'][name])
        if len(results) > 1:
            raise ExtraMatchesError
        if not results:
            raise NoMatchError
        else:
            return results[0]

    async def remove_alias_from_page(self, alias_name: str, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$unset': {
                    'aliases.{}'.format(alias_name): '',
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_alias_from_page {{{alias_name}}} from page {{{page_id}}}')

    async def remove_link_from_alias(self, link_id: ObjectId, alias_id: ObjectId):
        update_result: UpdateResult = await self.aliases.update_one(
            filter={'_id': alias_id},
            update={
                '$pull': {
                    'links': link_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_link_from_alias {{{link_id}}} from alias {{{alias_id}}}')

    async def remove_passive_link_from_alias(self, passive_link_id: ObjectId, alias_id: ObjectId):
        update_result: UpdateResult = await self.aliases.update_one(
            filter={'_id': alias_id},
            update={
                '$pull': {
                    'passive_links': passive_link_id,
                }
            }
        )
        self.assert_update_was_successful(update_result)
        self.log(f'remove_link_from_alias {{{passive_link_id}}} from alias {{{alias_id}}}')

    async def delete_alias(self, alias_id: ObjectId):
        delete_result: DeleteResult = await self.aliases.delete_one(
            filter={'_id': alias_id}
        )
        self.assert_delete_one_successful(delete_result)
        self.log(f'delete_alias {{{alias_id}}}')


class MongoDBMotorTornadoClient(MongoDBClient):  # pragma: no cover
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017, db_user=None, db_pass=None):
        from motor.motor_tornado import MotorClient
        super().__init__(MotorClient, db_name, db_host, db_port, db_user, db_pass)


class MongoDBMotorAsyncioClient(MongoDBClient):  # pragma: no cover
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017, db_user=None, db_pass=None):
        from motor.motor_asyncio import AsyncIOMotorClient
        super().__init__(AsyncIOMotorClient, db_name, db_host, db_port, db_user, db_pass)
