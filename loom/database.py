from bson.objectid import ObjectId
from motor.core import AgnosticClient, AgnosticDatabase, AgnosticCollection
from typing import Dict, List


class LoomMongoDBClient:
    def __init__(self, mongodb_client_class, collection='inkweaver', host='localhost', port=27017):
        self._host = host
        self._port = port
        self._client = mongodb_client_class(self.host, self.port)
        self._collection = getattr(self._client, collection)

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
    def collection(self) -> AgnosticDatabase:
        return self._collection

    @property
    def users(self) -> AgnosticCollection:
        return self.collection.users

    @property
    def stories(self) -> AgnosticCollection:
        return self.collection.stories

    @property
    def sections(self) -> AgnosticCollection:
        return self.collection.sections

    @property
    def wikis(self) -> AgnosticCollection:
        return self.collection.wikis

    @property
    def segments(self) -> AgnosticCollection:
        return self.collection.segments

    @property
    def pages(self) -> AgnosticCollection:
        return self.collection.pages

    @property
    def headings(self) -> AgnosticCollection:
        return self.collection.headings

    @property
    def content(self) -> AgnosticCollection:
        return self.collection.content

    @property
    def paragraphs(self) -> AgnosticCollection:
        return self.collection.paragraphs

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    async def create_user(self,
                          username: str,
                          password,  # TODO: Decide what this is.
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
            password: The salted hash of the user's password.
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
            'username':   username,
            'password':   password,
            'name':       name,
            'email':      email,
            'bio':        bio,
            'avatar':     avatar,
            'stories':    list(),
            'wikis':      list(),
            'statistics': None,
        }
        if _id is not None:
            user['_id'] = _id
        result = await self.users.insert_one(user)
        return result.inserted_id

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

    async def get_user_story_and_wiki_ids(self, user_id: ObjectId) -> Dict:
        """Grabs the ObjectIds of the user's stories.

        Args:
            user_id: BSON ObjectId of user to query for.

        Returns:
            A dict containing the BSON ObjectIds for the `stories` and
            `wikis` that the user has access to.

        """
        result = await self.users.find_one(
            filter={'_id': user_id},
            projection={
                '_id':     0,
                'stories': 1,
                'wikis':   1,
            }
        )
        return result

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

    async def create_section(self, title: str, content_id: ObjectId, _id=None) -> ObjectId:
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
            content_id: The unique ID of the list of paragraphs which go in this
                section before all the sub-sections.
            _id (ObjectId): `_id` is optional, but if provided will create a
                section with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created section. If
            `_id` was provided, `_id`, will be returned. Otherwise, the `_id`
            associated with the section will be returned.
        """
        section = {
            'title':         title,
            'content_id':    content_id,
            'pre_sections':  list(),
            'sections':      list(),
            'post_sections': list(),
            'statistics':    None,
        }
        if _id is not None:
            section['_id'] = _id
        result = await self.sections.insert_one(section)
        return result.inserted_id

    async def get_story_information(self, story_id: ObjectId):
        """Grabs the information associated with the provided story.

        Finds the story in the database and returns the document.

        Args:
            story_id: BSON ObjectId of story to query for.

        Returns:
            A copy of the document of the story.
        """
        result = await self.stories.find_one({'_id': story_id})
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
        the given `_id`, rather than the generated BSON Object Id. Currently,
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

    async def create_page(self, title: str, _id=None) -> ObjectId:
        """Inserts a new page to the pages collection.

        Adds a new page to the pages collection. Pages are leaf nodes in a tree
        that represent a wiki. Each page contains `headings`, which hold the
        content for a wiki page. `_id` is optional, and if provided will add a
        page to the collection with the given `_id`, otherwise a BSON ObjectId
        will be generated in its place. Currently, references and aliases are
        not implemented.

        Args:
            title: The title of the wiki page.
            _id (ObjectId): `_id` is optional, but if provided will create a
                page with the provided ObjectId.

        Returns:
            The ObjectId that is associated with the newly created page. If
            `_id` was provided, `_id`, will be returned. Otherwise, the `_id`
            associated with the page will be returned.

        """
        page = {
            'title':      title,
            'headings':   list(),
            'references': None,
            'aliases':    None,
        }
        if _id is not None:
            page['_id'] = _id
        result = await self.pages.insert_one(page)
        return result.inserted_id

    async def create_heading(self, title: str, content_id: ObjectId, _id=None) -> ObjectId:
        # TODO: Write header doc.
        """

        Args:
            title:
            content_id:
            _id:

        Returns:

        """
        heading = {
            'title': title,
            'content_id': content_id,
        }
        if _id is not None:
            heading['_id'] = _id
        result = await self.headings.insert_one(heading)
        return result.inserted_id

    ###########################################################################
    #
    # Content Methods
    #
    ###########################################################################

    async def create_content(self, _id=None) -> ObjectId:
        # TODO: Write header doc.
        """

        Args:
            _id:

        Returns:

        """
        content = {
            'paragraphs': list(),
        }
        if _id is not None:
            content['_id'] = _id
        result = await self.content.insert_one(content)
        return result.inserted_id

    async def create_paragraph(self, text: str, _id=None) -> ObjectId:
        # TODO: Write header doc.
        """

        Args:
            text:
            _id:

        Returns:

        """
        paragraph = {
            'text':       text,
            'statistics': None,
        }
        if _id is not None:
            paragraph['_id'] = _id
        result = await self.paragraphs.insert_one(paragraph)
        return result.inserted_id


class LoomMongoDBMotorTornadoClient(LoomMongoDBClient):
    def __init__(self, collection='inkweaver', host='localhost', port=27017):
        from motor.motor_tornado import MotorClient
        super().__init__(MotorClient, collection, host, port)


class LoomMongoDBMotorAsyncioClient(LoomMongoDBClient):
    def __init__(self, collection='inkweaver', host='localhost', port=27017):
        from motor.motor_asyncio import AsyncIOMotorClient
        super().__init__(AsyncIOMotorClient, collection, host, port)
