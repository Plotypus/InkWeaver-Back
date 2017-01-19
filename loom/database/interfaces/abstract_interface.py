from abc import ABC, abstractmethod

from passlib.hash import pbkdf2_sha512 as hasher


class AbstractDBInterface(ABC):

    # User object methods.

    @abstractmethod
    async def create_user(self, username, password, name, email):
        pass

    @staticmethod
    def hash_password(password):
        return hasher.hash(password)

    @staticmethod
    def verify_hash(text, hashed_text):
        return hasher.verify(text, hashed_text)

    @abstractmethod
    async def password_is_valid_for_username(self, username, password):
        pass

    @abstractmethod
    async def get_user_id_for_username(self, username):
        pass

    @abstractmethod
    async def get_user_preferences(self, user_id):
        pass

    @abstractmethod
    async def get_user_stories(self, user_id):
        pass

    @abstractmethod
    async def get_user_wikis(self, user_id):
        pass

    @abstractmethod
    async def set_user_password(self, user_id, password):
        pass

    @abstractmethod
    async def set_user_name(self, user_id, name):
        pass

    @abstractmethod
    async def set_user_email(self, user_id, email):
        pass

    @abstractmethod
    async def set_user_bio(self, user_id, bio):
        pass

    @abstractmethod
    async def set_user_avatar(self, user_id, avatar):
        pass

    # Story object methods.

    @abstractmethod
    async def create_story(self, user_id, title, summary, wiki_id):
        pass

    @abstractmethod
    async def create_section(self, title):
        pass

    @abstractmethod
    async def add_preceding_subsection(self, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_inner_subsection(self, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_succeeding_subsection(self, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_paragraph(self, section_id, text, index=None):
        pass

    @abstractmethod
    async def delete_story(self, story_id):
        pass

    @abstractmethod
    async def delete_section(self, section_id):
        pass

    @abstractmethod
    async def set_paragraph_text(self, section_id, index, text):
        pass

    @abstractmethod
    async def get_story(self, story_id):
        pass

    @abstractmethod
    async def get_story_hierarchy(self, story_id):
        pass

    @abstractmethod
    async def get_section_hierarchy(self, section_id):
        pass

    @abstractmethod
    async def get_section_content(self, section_id):
        pass

    # Wiki object methods.

    @abstractmethod
    async def create_wiki(self, user_id, title, summary):
        pass

    @abstractmethod
    async def create_segment(self, title):
        pass

    @abstractmethod
    async def create_page(self, title, parent_id):
        pass

    @abstractmethod
    async def add_child_segment(self, title, parent_id):
        pass

    @abstractmethod
    async def add_heading(self, title, page_id):
        pass

    @abstractmethod
    async def delete_wiki(self, wiki_id):
        pass

    @abstractmethod
    async def delete_segment(self, segment_id):
        pass

    @abstractmethod
    async def delete_page(self, page_id):
        pass

    @abstractmethod
    async def delete_heading(self, heading_title, page_id):
        pass

    @abstractmethod
    async def get_wiki(self, wiki_id):
        pass

    @abstractmethod
    async def get_wiki_hierarchy(self, wiki_id):
        pass

    @abstractmethod
    async def get_segment_hierarchy(self, segment_id):
        pass

    @abstractmethod
    async def get_segment(self, segment_id):
        pass

    @abstractmethod
    async def get_page(self, page_id):
        pass

    @abstractmethod
    async def get_heading(self, heading_id):
        pass
