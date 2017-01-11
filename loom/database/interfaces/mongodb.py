from .abstract import AbstractDBInterface

from loom.database.mongodb_clients import (
    LoomMongoDBClient,
    LoomMongoDBMotorTornadoClient,
    LoomMongoDBMotorAsyncioClient
)

from passlib.hash import pbkdf2_sha512 as hasher
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
        password_hash = self.hash_password(password)
        inserted_id = await self.client.create_user(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            bio=None,
            avatar=None
        )
        return inserted_id

    @staticmethod
    def hash_password(password):
        return hasher.hash(password)

    async def password_is_valid_for_username(self, username, password):
        stored_hash = await self.client.get_password_hash_for_username(username)
        return hasher.verify(password, stored_hash)

    async def get_user_preferences(self, user_id):
        preferences = await self.client.get_user_preferences(user_id)
        return preferences

    async def get_user_stories(self, user_id):
        story_ids = await self.client.get_user_story_ids(user_id)
        stories = await self._get_stories_or_wikis_by_ids(user_id, story_ids, 'story')
        return stories

    async def get_user_wikis(self, user_id):
        wiki_ids = await self.client.get_user_wiki_ids(user_id)
        wikis = await self._get_stories_or_wikis_by_ids(user_id, wiki_ids, 'wiki')
        return wikis

    @staticmethod
    def _get_current_user_access_level_in_object(user_id, obj):
        for user in obj['users']:
            if user['_id'] == user_id:
                return user['access_level']

    async def _get_stories_or_wikis_by_ids(self, user_id, object_ids, object_type):
        objects = []
        for object_id in object_ids:
            if object_type == 'story':
                obj = await self.client.get_story(object_id)
            elif object_type == 'wiki':
                obj = await self.client.get_wiki(object_id)
            else:
                raise ValueError("invalid object type: {}".format(object_type))
            access_level = self._get_current_user_access_level_in_object(user_id, obj)
            objects.append({
                'story_id':     obj['_id'],
                'title':        obj['title'],
                'access_level': access_level,
            })
        return objects

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
        story = await self.client.get_story(story_id)
        return story

    async def get_story_hierarchy(self, story_id):
        story = await self.get_story(story_id)
        section_id = story['section_id']
        return await self.get_section_hierarchy(section_id)

    async def get_section_hierarchy(self, section_id):
        section = await self.client.get_section(section_id)
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
        wiki = await self.client.get_wiki(wiki_id)
        return wiki

    async def get_wiki_hierarchy(self, wiki_id):
        wiki = await self.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self.get_segment_hierarchy(segment_id)

    async def get_segment_hierarchy(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        hierarchy = {
            'title':      segment['title'],
            'segment_id': segment_id,
            'segments':   [await self.get_segment_hierarchy(seg_id) for seg_id in segment['segments']],
            'pages':      [await self.get_page_for_hierarchy(page_id) for page_id in segment['pages']],
        }
        return hierarchy

    async def get_page_for_hierarchy(self, page_id):
        page = await self.client.get_page(page_id)
        return {
            'title':   page['title'],
            'page_id': page_id,
        }

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
