from bson.objectid import ObjectId
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection
from pymongo.results import UpdateResult
from typing import Dict, List


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
    def __init__(self, mongodb_client_class, db_name='inkweaver', db_host='localhost', db_port=27017):
        self._host = db_host
        self._port = db_port
        self._client = mongodb_client_class(self.host, self.port)
        self._database = getattr(self._client, db_name)

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
    def aliases(self) -> AgnosticCollection:
        return self.database.aliases

    async def drop_database(self):
        await self.client.drop_database(self.database)

    @staticmethod
    def assert_update_one_was_successful(update_result: UpdateResult):
        if update_result.matched_count == 0:
            raise NoMatchError
        if update_result.matched_count > 1:
            raise ExtraMatchesError
        if update_result.modified_count == 0:
            raise NoUpdateError
        if update_result.modified_count > 1:
            raise ExtraUpdatesError

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
        # TODO: Implement statistics.
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
        return result.inserted_id

    async def get_password_hash_for_username(self, username: str) -> str:
        user = await self.users.find_one(
            filter={'username': username},
            projection={
                'password_hash': 1,
            }
        )
        return user['password_hash']

    async def get_user_id_for_username(self, username: str) -> ObjectId:
        user = await self.users.find_one(
            filter={'username': username},
            projection={
                '_id': 1,
            }
        )
        return user['_id']

    async def add_story_to_user(self, user_id: ObjectId, story_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$push': {
                    'stories': story_id
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def add_wiki_to_user(self, user_id: ObjectId, wiki_id: ObjectId):
        update_result: UpdateResult = await self.users.update_one(
            filter={'_id': user_id},
            update={
                '$push': {
                    'wikis': wiki_id
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

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
        return result

    async def get_user_story_ids(self, user_id: ObjectId) -> List[ObjectId]:
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':     0,
                'stories': 1,
            }
        )
        return result['stories']

    async def get_user_wiki_ids(self, user_id: ObjectId) -> List[ObjectId]:
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':   0,
                'wikis': 1,
            }
        )
        return result['wikis']

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    async def create_story(self,
                           title: str,
                           wiki_id: ObjectId,
                           user_description,  # TODO: Decide what this is.
                           summary: str,
                           section_id: ObjectId,
                           _id=None) -> ObjectId:
        # TODO: Implement statistics and settings.
        story = {
            'title':      title,
            'wiki_id':    wiki_id,
            'users':      [user_description],
            'summary':    summary,
            'section_id': section_id,
            'statistics': None,
            'settings':   None,
        }
        if _id is not None:
            story['_id'] = _id
        result = await self.stories.insert_one(story)
        return result.inserted_id

    async def create_section(self, title: str, _id=None) -> ObjectId:
        # TODO: Implement statistics.
        section = {
            'title':                  title,
            'content':                list(),  # content is a list of "paragraph objects"
            'preceding_subsections':  list(),
            'inner_subsections':      list(),
            'succeeding_subsections': list(),
            'statistics':             None,
        }
        if _id is not None:
            section['_id'] = _id
        result = await self.sections.insert_one(section)
        return result.inserted_id

    @staticmethod
    def _insertion_parameters(object, position=None):
        inner_parameters = {
            '$each': [object],
        }
        if position is not None:
            inner_parameters['$position'] = position
        return inner_parameters

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
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

    async def insert_paragraph(self, paragraph_id: ObjectId, text: str, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters({
            '_id':        paragraph_id,
            'text':       text,
            'statistics': None,
        }, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'content': inner_parameters
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

    async def get_story(self, story_id: ObjectId) -> Dict:
        result = await self.stories.find_one({'_id': story_id})
        return result

    async def get_section(self, section_id: ObjectId) -> Dict:
        result = await self.sections.find_one({'_id': section_id})
        return result

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, title: str, user_description, summary: str, segment_id: ObjectId, _id=None) -> ObjectId:
        # TODO: Implement statistics and settings.
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
        return result.inserted_id

    async def create_segment(self, title: str, _id=None) -> ObjectId:
        # TODO: Implement statistics.
        segment = {
            'title':             title,
            'segments':          list(),
            'pages':             list(),
            'template_headings': list(),
            'statistics':        None,
        }
        if _id is not None:
            segment['_id'] = _id
        result = await self.segments.insert_one(segment)
        return result.inserted_id

    async def create_page(self, title: str, template_headings=None, _id=None) -> ObjectId:
        # TODO: Implement references and aliases.
        page = {
            'title':      title,
            'headings':   list() if template_headings is None else template_headings,
            'references': list(),  # list[Reference] (see Loom's wiki for more detail)
            'aliases':    list(),
        }
        if _id is not None:
            page['_id'] = _id
        result = await self.pages.insert_one(page)
        return result.inserted_id

    async def append_segment_to_parent_segment(self, child_segment: ObjectId, parent_segment: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': parent_segment},
            update={
                '$push': {
                    'segments': child_segment
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def append_page_to_parent_segment(self, page_id: ObjectId, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$push': {
                    'pages': page_id
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def append_template_heading_to_segment(self, title: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$push': {
                    # For now, this is the format of a `template_heading`
                    'template_headings': {
                        'title': title,
                        'text':  '',
                    }
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def insert_heading(self, title: str, page_id: ObjectId, at_index=None):
        heading = {
            'title': title,
            'text':  '',
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
        self.assert_update_one_was_successful(update_result)

    async def set_segment_title(self, title: str, segment_id: ObjectId):
        update_result: UpdateResult = await self.segments.update_one(
            filter={'_id': segment_id},
            update={
                '$set': {
                    'title': title
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

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
        self.assert_update_one_was_successful(update_result)

    async def get_wiki(self, wiki_id: ObjectId) -> Dict:
        result = await self.wikis.find_one({'_id': wiki_id})
        return result

    async def get_segment(self, segment_id: ObjectId) -> Dict:
        result = await self.segments.find_one({'_id': segment_id})
        return result

    async def get_page(self, page_id: ObjectId) -> Dict:
        result = await self.pages.find_one({'_id': page_id})
        return result

    async def get_template_heading(self, title: str, segment_id: ObjectId):
        result = await self.segments.find_one({
            '_id':                     segment_id,
            'template_headings.title': title
        })
        return result

    async def get_heading(self, title: str, page_id: ObjectId):
        result = await self.pages.find_one({
            '_id':            page_id,
            'headings.title': title
        })
        return result

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    async def create_link(self, context: Dict, alias_id: ObjectId, _id=None) -> ObjectId:
        link = {
            'context':  context,
            'alias_id': alias_id,
        }
        if _id is not None:
            link['_id'] = _id
        result = await self.links.insert_one(link)
        return result.inserted_id

    async def get_link(self, link_id: ObjectId):
        result = await self.links.find_one({'_id': link_id})
        return result

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    async def create_alias(self, name: str, page_id: ObjectId, _id=None) -> ObjectId:
        alias = {
            'name': name,
            'page_id': page_id,
        }
        if _id is not None:
            alias['_id'] = _id
        result = await self.aliases.insert_one(alias)
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
        self.assert_update_one_was_successful(update_result)

    async def get_alias(self, alias_id: ObjectId):
        result = await self.aliases.find_one({'_id': alias_id})
        return result


class MongoDBMotorTornadoClient(MongoDBClient):
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017):
        from motor.motor_tornado import MotorClient
        super().__init__(MotorClient, db_name, db_host, db_port)


class MongoDBMotorAsyncioClient(MongoDBClient):
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017):
        from motor.motor_asyncio import AsyncIOMotorClient
        super().__init__(AsyncIOMotorClient, db_name, db_host, db_port)
