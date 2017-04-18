from abc import ABC, abstractmethod

from passlib.hash import pbkdf2_sha512 as hasher


class AbstractDBInterface(ABC):

    ###########################################################################
    #
    # Database Methods
    #
    ###########################################################################

    @abstractmethod
    async def drop_database(self):
        pass

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

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
    async def get_user_stories_and_wikis(self, user_id):
        pass

    @abstractmethod
    async def get_story_description(self, user_id, story_id):
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

    @abstractmethod
    async def set_story_position_context(self, user_id, story_id, position_context):
        pass

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

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
    async def add_paragraph(self, wiki_id, section_id, text, succeeding_paragraph_id=None):
        pass

    @abstractmethod
    async def add_bookmark(self, name, story_id, section_id, paragraph_id, index=None):
        pass

    @abstractmethod
    async def add_story_collaborator(self, story_id, username):
        pass

    @abstractmethod
    async def get_story(self, story_id):
        pass

    @abstractmethod
    async def get_story_bookmarks(self, story_id):
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

    @abstractmethod
    async def set_story_title(self, story_id, title):
        pass

    @abstractmethod
    async def set_section_title(self, section_id, title):
        pass

    @abstractmethod
    async def set_paragraph_text(self, wiki_id, section_id, text, paragraph_id):
        pass

    @abstractmethod
    async def set_bookmark_name(self, story_id, bookmark_id, new_name):
        pass

    @abstractmethod
    async def set_note(self, section_id, paragraph_id, text):
        pass

    @abstractmethod
    async def delete_story(self, story_id, user_id):
        pass

    @abstractmethod
    async def delete_section(self, section_id):
        pass

    @abstractmethod
    async def delete_paragraph(self, section_id, paragraph_id):
        pass

    @abstractmethod
    async def delete_note(self, section_id, paragraph_id):
        pass

    @abstractmethod
    async def delete_bookmark(self, bookmark_id):
        pass

    @abstractmethod
    async def remove_story_collaborator(self, story_id, user_id):
        pass

    @abstractmethod
    async def move_subsection_as_preceding(self, section_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_subsection_as_inner(self, section_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_subsection_as_succeeding(self, section_id, to_parent_id, to_index):
        pass

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_wiki(self, user_id, title, summary):
        pass

    @abstractmethod
    async def create_segment(self, title):
        pass

    @abstractmethod
    async def create_page(self, wiki_id, title, parent_id):
        pass

    @abstractmethod
    async def add_child_segment(self, wiki_id, title, parent_id):
        pass

    @abstractmethod
    async def add_template_heading(self, title, segment_id):
        pass

    @abstractmethod
    async def add_heading(self, title, page_id, index=None):
        pass

    @abstractmethod
    async def add_wiki_collaborator(self, wiki_id, username):
        pass

    @abstractmethod
    async def get_wiki(self, wiki_id):
        pass

    @abstractmethod
    async def get_wiki_alias_list(self, wiki_id):
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
    async def get_segment_summary(self, segment_id):
        pass

    @abstractmethod
    async def get_page_for_frontend(self, page_id):
        pass

    @abstractmethod
    async def get_page_summary(self, page_id):
        pass

    @abstractmethod
    async def set_wiki_title(self, title, wiki_id):
        pass

    @abstractmethod
    async def set_segment_title(self, title, segment_id):
        pass

    @abstractmethod
    async def set_template_heading_title(self, old_title, new_title, segment_id):
        pass

    @abstractmethod
    async def set_template_heading_text(self, title, text, segment_id):
        pass

    @abstractmethod
    async def set_page_title(self, wiki_id, new_title, page_id):
        pass

    @abstractmethod
    async def set_heading_title(self, old_title, new_title, page_id):
        pass

    @abstractmethod
    async def set_heading_text(self, title, text, page_id):
        pass

    @abstractmethod
    async def delete_wiki(self, user_id, wiki_id):
        pass

    @abstractmethod
    async def delete_segment(self, wiki_id, segment_id):
        pass

    @abstractmethod
    async def delete_template_heading(self, title, segment_id):
        pass

    @abstractmethod
    async def delete_page(self, wiki_id, page_id):
        pass

    @abstractmethod
    async def delete_heading(self, heading_title, page_id):
        pass

    @abstractmethod
    async def remove_wiki_collaborator(self, wiki_id, user_id):
        pass

    @abstractmethod
    async def move_segment(self, segment_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_template_heading(self, segment_id, template_heading_title, to_index):
        pass

    @abstractmethod
    async def move_page(self, page_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_heading(self, page_id, heading_title, to_index):
        pass

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_link(self, story_id, section_id, paragraph_key, name, page_id):
        pass

    @abstractmethod
    async def get_link(self, link_id):
        pass

    @abstractmethod
    async def delete_link(self, link_id):
        pass

    ###########################################################################
    #
    # Passive Link Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_passive_link(self, section_id, paragraph_id, alias_id, page_id):
        pass

    @abstractmethod
    async def get_passive_link(self, passive_link_id):
        pass

    @abstractmethod
    async def approve_passive_link(self, passive_link_id, story_id, wiki_id):
        pass

    @abstractmethod
    async def reject_passive_link(self, passive_link_id):
        pass

    @abstractmethod
    async def delete_passive_link(self, passive_link_id):
        pass

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_alias(self, name, page_id):
        pass

    @abstractmethod
    async def get_alias(self, alias_id):
        pass

    @abstractmethod
    async def change_alias_name(self, wiki_id, alias_id, name):
        pass

    @abstractmethod
    async def delete_alias(self, wiki_id, alias_id):
        pass

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    @abstractmethod
    async def get_story_statistics(self, story_id):
        pass

    @abstractmethod
    async def get_section_statistics_recursive(self, section_id):
        pass

    @abstractmethod
    async def get_paragraph_statistics(self, section_id, paragraph_id):
        pass

    @abstractmethod
    async def get_page_frequencies_in_story(self, story_id, wiki_id):
        pass
