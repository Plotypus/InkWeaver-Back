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
        """Inserts a new user to the users collection.

        Adds a new user to the `users` collection. Stories and wikis are
        initialized to empty lists. Unless `_id` is provided, a random BSON
        ObjectId will be assigned to `_id`.

        Args:
            username: The username of the user.
            password_hash: The hash of the user's password.
            name: The full name of the user.
            email: The email address of the user.
            bio: A short description of the user.
            avatar (str): Base-64 encoded image user chooses to identify
                themselves with.
            _id (ObjectId): `_id` is optional, but if provided, will create a
                user with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created user. If
            `_id` was provided, `_id` will be returned. Otherwise, a randomly
            generated BSON ObjectId will be returned.

        """
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
        """

        :param user_id:
        :return:
        """
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
        """Grabs the preferences for the provided user.

        Finds the user in the database and extracts the fields specified by
        The LAW Protocol.

        Args:
            user_id: BSON ObjectId of user to query for.

        Returns:
            A filtered document of the user. According to the LAW Protocol,
            returns `username`, `name`, `email`, `bio`, and `avatar` of the
            user.

        """
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
        """Grabs the ObjectIds of the user's stories.

        Args:
            user_id: BSON ObjectId of user to query for.

        Returns:
            A list of the BSON ObjectIds of the `stories` that the user has
            access to.

        """
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':     0,
                'stories': 1,
            }
        )
        return result['stories']

    async def get_user_wiki_ids(self, user_id: ObjectId) -> List[ObjectId]:
        """Grabs the ObjectIds of the user's wikis.

        Args:
            user_id: BSON ObjectId of user to query for.

        Returns:
            A list of the BSON ObjectIds of the `wikis` that the user has
            access to.

        """
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
        """Inserts a new story to the stories collection.

        Adds a new story to the stories collection. A section for the story
        should be created before calling this function, in which the
        `section_id` is specified. `_id` is optional and if provided will
        create the story with the given `_id`, rather than the generated BSON
        ObjectId. Currently, statistics and settings are unimplemented.

        Args:
            title: The title of the story.
            wiki_id: The unique ID of the associated wiki.
            user_description: A dict containing information of the story's
                owner. A user description contains a `user_id`, `name`, and
                `access_level`.

                `user_description` args:
                    user_id (ObjectId): The unique ID of the user.
                    name (str): The name of the user.
                    access_level (str): A description of the user's
                        privileges in the story.
            summary: A brief summary of the story.
            section_id: The unique ID of the story's recursive section
                representation.
            _id (ObjectId): `_id` is optional, but if provided will create a
                story with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created story. If
            `_id` was provided, `_id` will be returned. Otherwise, a randomly
            generated BSON ObjectId will be returned.

        """
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
        """Inserts a new section to the sections collection.

        Adds a new section to the sections collection. Sections are nodes in a
        tree that represent a story. Each section can contain text (content) and
        also sub-sections. As a leaf node, sections can be thought of as a
        chapter. Pre-sections can be used to represent a prologue and
        post-sections an epilogue. `_id` is optional, and if provided will add a
        section to the collection with the given `_id`, otherwise a BSON
        ObjectId will be generated in its place. Currently, statistics are not
        implemented.

        Args:
            title: The title of the section.
            _id (ObjectId): `_id` is optional, but if provided will create a
                section with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created section. If
            `_id` was provided, `_id`, will be returned. Otherwise, the `_id`
            associated with the section will be returned.

        """
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

    async def insert_paragraph(self, text: str, to_section_id, at_index=None):
        inner_parameters = self._insertion_parameters({'text': text, 'statistics': None}, at_index)
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': to_section_id},
            update={
                '$push': {
                    'content': inner_parameters
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def set_paragraph_text(self, text: str, in_section_id: ObjectId, at_index: int):
        update_result: UpdateResult = await self.sections.update_one(
            filter={'_id': in_section_id},
            update={
                '$set': {
                    # Look in the content array of the matching section. Find the object by index using `.index`.
                    # Set the `.text` field to `paragraph`.
                    'content.{}.text'.format(at_index): text
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def get_story(self, story_id: ObjectId) -> Dict:
        """Grabs the information associated with the provided story.

        Finds the story in the database and returns the document.

        Args:
            story_id: BSON ObjectId of story to query for.

        Returns:
            A copy of the document of the story.

        """
        result = await self.stories.find_one({'_id': story_id})
        return result

    async def get_section(self, section_id: ObjectId) -> Dict:
        # TODO: Add docstring
        """

        Args:
            section_id:

        Returns:

        """
        result = await self.sections.find_one({'_id': section_id})
        return result

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, title: str, user_description, summary: str, segment_id: ObjectId, _id=None) -> ObjectId:
        """Inserts a new wiki to the wikis collection.

        Adds a new wiki to the wikis collection. A segment for the wiki should
        be created before calling this function, in which the `segment_id` is
        specified. `_id` is optional and if provided will create the wiki with
        the given `_id`, rather than the generated BSON ObjectId. Currently,
        statistics and settings are unimplemented.

        Args:
            title: The title of the wiki.
            user_description: A dict containing the information of the wiki's
                owner. A user description contains a `user_id`, `name`, and
                `access_level`.

                `user_description` args:
                    user_id (ObjectId): The unique ID of the user.
                    name (str): The name of the user.
                    access_level (str): A description of the user's privileges
                    in the story.
            summary: A brief summary of the the wiki.
            segment_id: The unique ID of the wiki's recursive segment
                representation.
            _id (ObjectId): `_id` is optional, but if provided will create a
                wiki with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created wiki. If
            `_id` was provided, `_id` will be returned. Otherwise, a randomly
            generated BSON ObjectId will be returned.

        """
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
        """Inserts a new segment to the segments collection.

        Adds a new segment to the segments collection. Segments are nodes in a
        tree that represent a wiki. Each segment can contain sub-segments and
        pages. Segments can be thought of as non-leaf nodes in the tree, where
        pages are the leaf nodes. `template_headings` track headings that are
        added to pages when pages are first created. Note, `template_headings`
        only apply to pages directly under this segment. `_id` is optional, and
        if provided will add a segment to the collection with the given `_id`,
        otherwise a BSON ObjectId will be generated in its place. Currently,
        statistics are not implemented.

        Args:
            title: The title of the wiki segment.
            _id (ObjectId): `_id` is optional, but if provided will create a
                segment with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created segment. If
            `_id` was provided, `_id`, will be returned. Otherwise, the `_id`
            associated with the segment will be returned.

        """
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
        """Inserts a new page to the pages collection.

        Adds a new page to the pages collection. Pages are leaf nodes in a tree
        that represent a wiki. Each page contains `headings`, which hold the
        content for a wiki page. `_id` is optional, and if provided will add a
        page to the collection with the given `_id`, otherwise a BSON ObjectId
        will be generated in its place. Currently, references and aliases are
        not implemented.

        Args:
            title: The title of the wiki page.
            template_headings (List[Dict]): The list of template headings to
                inherit.
            _id (ObjectId): `_id` is optional, but if provided will create a
                page with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created page. If
            `_id` was provided, `_id`, will be returned. Otherwise, the `_id`
            associated with the page will be returned.

        """
        # TODO: Implement references and aliases.
        page = {
            'title':      title,
            'headings':   list() if template_headings is None else template_headings,
            'references': None,
            'aliases':    None,
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
                        'title':   title,
                        'content': list(),
                    }
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def append_heading_to_page(self, title: str, page_id: ObjectId):
        update_result: UpdateResult = await self.pages.update_one(
            filter={'_id': page_id},
            update={
                '$push': {
                    'headings': {
                        'title': title,
                        'text':  "",
                    }
                }
            }
        )
        self.assert_update_one_was_successful(update_result)

    async def get_wiki(self, wiki_id: ObjectId) -> Dict:
        """Grabs the information associated with the provided wiki.

        Finds the wiki in the database and returns the document.

        Args:
            wiki_id: BSON ObjectId of wiki to query for.

        Returns:
            A copy of the document of the wiki.

        """
        result = await self.wikis.find_one({'_id': wiki_id})
        return result

    async def get_segment(self, segment_id: ObjectId) -> Dict:
        """Grabs the information associated with the provided segment.

        Finds the segment in the database and returns the document.

        Args:
            segment_id: BSON ObjectId of segment to query for.

        Returns:
            A copy of the document of the segment.

        """
        result = await self.segments.find_one({'_id': segment_id})
        return result

    async def get_page(self, page_id: ObjectId) -> Dict:
        """Grabs the information associated with the provided page.

        Finds the page in the database and returns the document.

        Args:
            page_id: BSON ObjectId of page to query for.

        Returns:
            A copy of the document of the page.

        """
        result = await self.pages.find_one({'_id': page_id})
        return result

class MongoDBMotorTornadoClient(MongoDBClient):
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017):
        from motor.motor_tornado import MotorClient
        super().__init__(MotorClient, db_name, db_host, db_port)


class MongoDBMotorAsyncioClient(MongoDBClient):
    def __init__(self, db_name='inkweaver', db_host='localhost', db_port=27017):
        from motor.motor_asyncio import AsyncIOMotorClient
        super().__init__(AsyncIOMotorClient, db_name, db_host, db_port)
