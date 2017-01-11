from .abstract import AbstractDBInterface

from loom.database.mongodb_clients import LoomMongoDBClient, LoomMongoDBMotorTornadoClient, LoomMongoDBMotorAsyncioClient

from typing import ClassVar


class MongoDBInterface(AbstractDBInterface):
    def __init__(self, db_client_class: ClassVar, db_name, db_host, db_port):
        if not issubclass(db_client_class, LoomMongoDBClient):
            raise ValueError("invalid MongoDB client class: {}".format(db_client_class.__name__))
        self._client = db_client_class(db_name, db_host, db_port)

    @property
    def client(self):
        return self._client

    # User object methods.

    async def create_user(self, username, password, name, email):
        pass

    async def get_user_preferences(self, user_id):
        pass

    async def get_user_stories(self, user_id):
        pass

    async def get_user_wikis(self, user_id):
        pass

    async def set_user_password(self, user_id, password):
        pass

    async def set_user_name(self, user_id, name):
        pass

    async def set_user_email(self, user_id, email):
        pass

    async def set_user_bio(self, user_id, bio):
        pass

    async def set_user_avatar(self, user_id, avatar):
        pass

    # Story object methods.

    async def create_story(self, user_id, title, summary, wiki_id):
        pass

    async def create_preceding_subsection(self, title, in_parent_section):
        pass

    async def create_inner_subsection(self, title, in_parent_section):
        pass

    async def create_succeeding_subsection(self, title, in_parent_section):
        pass

    async def create_section(self, title):
        pass

    async def get_story(self, story_id):
        pass

    async def get_story_hierarchy(self, story_id):
        pass

    async def get_section_hierarchy(self, section_id):
        pass

    async def get_section_content(self, section_id):
        pass

    # Wiki object methods.

    async def create_wiki(self, user_id, title, summary):
        pass

    async def create_child_segment(self, title, in_parent_segment):
        pass

    async def create_segment(self, title):
        pass

    async def create_page(self, title, in_parent_segment):
        pass

    async def create_heading(self, title, page_id):
        pass

    async def get_wiki(self, wiki_id):
        pass

    async def get_wiki_hierarchy(self, wiki_id):
        pass

    async def get_segment_hierarchy(self, segment_id):
        pass

    async def get_segment(self, segment_id):
        pass

    async def get_page(self, page_id):
        pass

    async def get_heading(self, heading_id):
        pass


class MongoDBTornadoInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port):
        super().__init__(LoomMongoDBMotorTornadoClient, db_name, db_host, db_port)


class MongoDBAsyncioInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port):
        super().__init__(LoomMongoDBMotorAsyncioClient, db_name, db_host, db_port)
