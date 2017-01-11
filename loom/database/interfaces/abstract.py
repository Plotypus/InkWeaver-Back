from abc import ABC, abstractmethod, abstractproperty


class AbstractDBInterface(ABC):

    # User object methods.

    @abstractmethod
    async def create_user(self, username, password, name, email):
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
    async def create_preceding_subsection(self, title, in_parent_section):
        pass

    @abstractmethod
    async def create_inner_subsection(self, title, in_parent_section):
        pass

    @abstractmethod
    async def create_succeeding_subsection(self, title, in_parent_section):
        pass

    @abstractmethod
    async def create_section(self, title):
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
    async def create_child_segment(self, title, in_parent_segment):
        pass

    @abstractmethod
    async def create_segment(self, title):
        pass

    @abstractmethod
    async def create_page(self, title, in_parent_segment):
        pass

    @abstractmethod
    async def create_heading(self, title, page_id):
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

    # Content object methods.

    @abstractmethod
    async def create_content(self):
        pass

    @abstractmethod
    async def create_paragraph(self, text):
        pass

    @abstractmethod
    async def get_content(self, content_id):
        pass

    @abstractmethod
    async def get_paragraph(self, paragraph_id):
        pass
