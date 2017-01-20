from .abstract_interface import AbstractDBInterface

from loom.database.clients import *

from bson.objectid import ObjectId
from typing import ClassVar


class MongoDBInterface(AbstractDBInterface):
    def __init__(self, db_client_class: ClassVar, db_name, db_host, db_port):
        if not issubclass(db_client_class, MongoDBClient):
            raise ValueError("invalid MongoDB client class: {}".format(db_client_class.__name__))
        self._client = db_client_class(db_name, db_host, db_port)

    @property
    def client(self):
        return self._client

    # User object methods.

    async def create_user(self, username, password, name, email):
        # TODO: Check the username is not currently in use.
        password_hash = super().hash_password(password)
        inserted_id = await self.client.create_user(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            bio=None,
            avatar=None
        )
        return inserted_id

    async def password_is_valid_for_username(self, username, password):
        stored_hash = await self.client.get_password_hash_for_username(username)
        return super().verify_hash(password, stored_hash)

    async def get_user_id_for_username(self, username):
        user_id = await self.client.get_user_id_for_username(username)
        return user_id

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
            if user['user_id'] == user_id:
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
            id_key = '{}_id'.format(object_type)
            objects.append({
                id_key:         obj['_id'],
                'title':        obj['title'],
                'access_level': access_level,
            })
        return objects

    async def set_user_password(self, user_id, password):
        # TODO: Check the password is not equal to the previous password.
        password_hash = super().hash_password(password)
        await self.client.set_user_password_hash(user_id, password_hash)

    async def set_user_name(self, user_id, name):
        await self.client.set_user_name(user_id, name)

    async def set_user_email(self, user_id, email):
        await self.client.set_user_email(user_id, email)

    async def set_user_bio(self, user_id, bio):
        await self.client.set_user_bio(user_id, bio)

    async def set_user_avatar(self, user_id, avatar):
        await self.client.set_user_avatar(user_id, avatar)

    # Story object methods.

    async def create_story(self, user_id, title, summary, wiki_id) -> ObjectId:
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        section_id = await self.create_section(title)
        inserted_id = await self.client.create_story(title, wiki_id, user_description, summary, section_id)
        await self.client.add_story_to_user(user_id, inserted_id)
        return inserted_id

    async def create_section(self, title) -> ObjectId:
        inserted_id = await self.client.create_section(title)
        return inserted_id

    async def delete_story(self, story_id):
        # TODO: Do this.
        pass

    async def delete_section(self, section_id):
        # TODO: Do this.
        pass

    async def add_preceding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_preceding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_inner_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_inner_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_succeeding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_succeeding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_paragraph(self, section_id, text, index=None):
        return await self.client.insert_paragraph(text, to_section_id=section_id, at_index=index)

    async def set_paragraph_text(self, section_id, index, text):
        return await self.client.set_paragraph_text(text, in_section_id=section_id, at_index=index)

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
        section = await self.client.get_section(section_id)
        return section['content']

    # Wiki object methods.

    async def create_wiki(self, user_id, title, summary):
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        segment_id = await self.create_segment(title)
        inserted_id = await self.client.create_wiki(title, user_description, summary, segment_id)
        await self.client.add_wiki_to_user(user_id, inserted_id)
        return inserted_id

    async def create_segment(self, title):
        inserted_id = await self.client.create_segment(title)
        return inserted_id

    async def create_page(self, title, in_parent_segment):
        # Create the page and include the `template_headings` from the parent
        parent_segment = await self.get_segment(in_parent_segment)
        template_headings = parent_segment['template_headings']
        page_id = await self.client.create_page(title, template_headings)
        try:
            await self.client.append_page_to_parent_segment(page_id, in_parent_segment)
        except ClientError:
            self.delete_page(page_id)
        else:
            return page_id

    async def add_child_segment(self, title, parent_id):
        child_segment_id = await self.create_segment(title)
        try:
            await self.client.append_segment_to_parent_segment(child_segment_id, parent_id)
        except ClientError:
            self.delete_segment(child_segment_id)
        else:
            return child_segment_id

    async def add_template_heading(self, title, segment_id):
        try:
            await self.client.append_template_heading_to_segment(title, segment_id)
        except ClientError:
            # TODO: Deal with this.
            raise
        else:
            # TODO: Should this return something?
            pass

    async def add_heading(self, title, page_id):
        try:
            await self.client.append_heading_to_page(title, page_id)
        except ClientError:
            # TODO: Deal with this.
            raise
        else:
            # TODO: Should this return something?
            pass

    async def delete_wiki(self, wiki_id):
        # TODO: Implement this.
        pass

    async def delete_segment(self, segment_id):
        # TODO: Implement this.
        pass

    async def delete_page(self, page_id):
        # TODO: Implement this.
        pass

    async def delete_heading(self, heading_title, page_id):
        # TODO: Implement this.
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
        segment = await self.client.get_segment(segment_id)
        return segment

    async def get_page(self, page_id):
        page = await self.client.get_page(page_id)
        return page

    async def get_heading(self, heading_id):
        pass


class MongoDBTornadoInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port):
        super().__init__(MongoDBMotorTornadoClient, db_name, db_host, db_port)


class MongoDBAsyncioInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port):
        super().__init__(MongoDBMotorAsyncioClient, db_name, db_host, db_port)
