from abc import ABC, abstractmethod


class AbstractDispatcher(ABC):

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    @abstractmethod
    async def get_user_preferences(self, uuid, message_id, user_id):
        pass

    @abstractmethod
    async def get_user_stories_and_wikis(self, uuid, message_id, user_id):
        pass

    @abstractmethod
    async def set_user_name(self, uuid, message_id, user_id, name):
        pass

    @abstractmethod
    async def set_user_email(self, uuid, message_id, user_id, email):
        pass

    @abstractmethod
    async def set_user_bio(self, uuid, message_id, user_id, bio):
        pass

    # TODO: Implement this at some point.
    # @abstractmethod
    # async def set_user_avatar(self, uuid, message_id, avatar):
    #     pass

    @abstractmethod
    async def set_user_story_position_context(self, uuid, message_id, user_id, story_id, position_context):
        pass

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_story(self, uuid, message_id, user_id, title, wiki_id, summary):
        pass

    @abstractmethod
    async def add_preceding_subsection(self, uuid, message_id, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_inner_subsection(self, uuid, message_id, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_succeeding_subsection(self, uuid, message_id, title, parent_id, index=None):
        pass

    @abstractmethod
    async def add_paragraph(self, uuid, message_id, wiki_id, section_id, text, succeeding_paragraph_id=None):
        pass

    @abstractmethod
    async def add_bookmark(self, uuid, message_id, name, story_id, section_id, paragraph_id, index=None):
        pass

    @abstractmethod
    async def edit_story(self, uuid, message_id, story_id, update):
        pass

    @abstractmethod
    async def edit_paragraph(self, uuid, message_id, wiki_id, section_id, update, paragraph_id):
        pass

    @abstractmethod
    async def edit_section_title(self, uuid, message_id, section_id, new_title):
        pass

    @abstractmethod
    async def edit_bookmark(self, uuid, message_id, story_id, bookmark_id, update):
        pass

    @abstractmethod
    async def set_note(self, uuid, message_id, section_id, paragraph_id, note):
        pass

    @abstractmethod
    async def get_story_information(self, uuid, message_id, story_id):
        pass

    @abstractmethod
    async def get_story_bookmarks(self, uuid, message_id, story_id):
        pass

    @abstractmethod
    async def get_story_hierarchy(self, uuid, message_id, story_id):
        pass

    @abstractmethod
    async def get_section_hierarchy(self, uuid, message_id, section_id):
        pass

    @abstractmethod
    async def get_section_content(self, uuid, message_id, section_id):
        pass

    @abstractmethod
    async def delete_story(self, uuid, message_id, story_id):
        pass

    @abstractmethod
    async def delete_section(self, uuid, message_id, section_id):
        pass

    @abstractmethod
    async def delete_paragraph(self, uuid, message_id, section_id, paragraph_id):
        pass

    @abstractmethod
    async def delete_note(self, uuid, message_id, section_id, paragraph_id):
        pass

    @abstractmethod
    async def delete_bookmark(self, uuid, message_id, bookmark_id):
        pass

    @abstractmethod
    async def move_subsection_as_preceding(self, uuid, message_id, section_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_subsection_as_inner(self, uuid, message_id, section_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_subsection_as_succeeding(self, uuid, message_id, section_id, to_parent_id, to_index):
        pass

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    @abstractmethod
    async def create_wiki(self, uuid, message_id, user_id, title, summary):
        pass

    @abstractmethod
    async def add_segment(self, uuid, message_id, wiki_id, title, parent_id):
        pass

    @abstractmethod
    async def add_template_heading(self, uuid, message_id, title, segment_id):
        pass

    @abstractmethod
    async def add_page(self, uuid, message_id, wiki_id, title, parent_id):
        pass

    @abstractmethod
    async def add_heading(self, uuid, message_id, title, page_id, index=None):
        pass

    @abstractmethod
    async def edit_wiki(self, uuid, message_id, wiki_id, update):
        pass

    @abstractmethod
    async def edit_segment(self, uuid, message_id, segment_id, update):
        pass

    @abstractmethod
    async def edit_template_heading(self, uuid, message_id, segment_id, template_heading_title, update):
        pass

    @abstractmethod
    async def edit_page(self, uuid, message_id, wiki_id, page_id, update):
        pass

    @abstractmethod
    async def edit_heading(self, uuid, message_id, page_id, heading_title, update):
        pass

    @abstractmethod
    async def get_wiki_information(self, uuid, message_id, wiki_id):
        pass

    @abstractmethod
    async def get_wiki_hierarchy(self, uuid, message_id, wiki_id):
        pass

    @abstractmethod
    async def get_wiki_segment_hierarchy(self, uuid, message_id, segment_id):
        pass

    @abstractmethod
    async def get_wiki_segment(self, uuid, message_id, segment_id):
        pass

    @abstractmethod
    async def get_wiki_page(self, uuid, message_id, page_id):
        pass

    @abstractmethod
    async def delete_wiki(self, uuid, message_id, user_id, wiki_id):
        pass

    @abstractmethod
    async def delete_segment(self, uuid, message_id, wiki_id, segment_id):
        pass

    @abstractmethod
    async def delete_template_heading(self, uuid, message_id, segment_id, template_heading_title):
        pass

    @abstractmethod
    async def delete_page(self, uuid, message_id, wiki_id, page_id):
        pass

    @abstractmethod
    async def delete_heading(self, uuid, message_id, heading_title, page_id):
        pass

    @abstractmethod
    async def move_segment(self, uuid, message_id, segment_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_template_heading(self, uuid, message_id, segment_id, template_heading_title, to_index):
        pass

    @abstractmethod
    async def move_page(self, uuid, message_id, page_id, to_parent_id, to_index):
        pass

    @abstractmethod
    async def move_heading(self, uuid, message_id, page_id, heading_title, to_index):
        pass

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    @abstractmethod
    async def delete_link(self, uuid, message_id, link_id):
        pass

    ###########################################################################
    #
    # Passive Link Methods
    #
    ###########################################################################

    @abstractmethod
    async def approve_passive_link(self, uuid, message_id, passive_link_id, story_id, wiki_id):
        pass

    @abstractmethod
    async def reject_passive_link(self, uuid, message_id, passive_link_id):
        pass

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    @abstractmethod
    async def change_alias_name(self, uuid, message_id, wiki_id, alias_id, new_name):
        pass

    @abstractmethod
    async def delete_alias(self, uuid, message_id, wiki_id, alias_id):
        pass

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    @abstractmethod
    async def get_story_statistics(self, uuid, message_id, story_id):
        pass

    @abstractmethod
    async def get_section_statistics(self, uuid, message_id, section_id):
        pass

    @abstractmethod
    async def get_paragraph_statistics(self, uuid, message_id, section_id, paragraph_id):
        pass

    @abstractmethod
    async def approve_passive_link(self, uuid, message_id, passive_link_id, story_id, wiki_id):
        pass

