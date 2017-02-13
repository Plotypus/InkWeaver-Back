from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWikiMessage(Message):
    _required_fields = [
        'message_id',
        'title',
        'summary',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def summary(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.create_wiki(self.message_id, self.title, self.summary)


###########################################################################
#
# Add Messages
#
###########################################################################
class AddSegmentMessage(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def parent_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.add_segment(self.message_id, self.title, self.parent_id)


class AddTemplateHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'title',
        'segment_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.add_template_heading(self.message_id, self.title, self.segment_id)


class AddPageMessage(Message):
    _required_fields = [
        'message_id',
        'title',
        'parent_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def parent_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.add_page(self.message_id, self.title, self.parent_id)


class AddHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'title',
        'page_id',
    ]
    _optional_fields = [
        'index'
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def title(self) -> str: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    @auto_getattr
    def index(self) -> int: pass

    def dispatch(self):
        return self._dispatcher.add_heading(self.message_id, self.title, self.page_id, self.index)


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditSegmentMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
        'update',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    @auto_getattr
    def update(self) -> dict: pass

    def dispatch(self):
        return self._dispatcher.edit_segment(self.message_id, self.segment_id, self.update)


class EditTemplateHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
        'template_heading_title'
        'update',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    @auto_getattr
    def template_heading_title(self) -> str: pass

    @auto_getattr
    def update(self) -> dict: pass

    def dispatch(self):
        return self._dispatcher.edit_template_heading(self.message_id, self.segment_id, self.template_heading_title,
                                               self.update)


class EditPageMessage(Message):
    _required_fields = [
        'message_id',
        'page_id',
        'update',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    @auto_getattr
    def update(self) -> dict: pass

    def dispatch(self):
        return self._dispatcher.edit_page(self.message_id, self.page_id, self.update)


class EditHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'page_id',
        'heading_title',
        'update',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    @auto_getattr
    def heading_title(self) -> str: pass

    @auto_getattr
    def update(self) -> dict: pass

    def dispatch(self):
        return self._dispatcher.edit_heading(self.message_id, self.page_id, self.heading_title, self.update)


###########################################################################
#
# Get Messages
#
###########################################################################
class GetWikiInformationMessage(Message):
    _required_fields = [
        'message_id',
        'wiki_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_wiki_information(self.message_id, self.wiki_id)


class GetWikiHierarchyMessage(Message):
    _required_fields = [
        'message_id',
        'wiki_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_wiki_hierarchy(self.message_id, self.wiki_id)


class GetWikiSegmentHierarchyMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_wiki_segment_hierarchy(self.message_id, self.segment_id)


class GetWikiSegmentMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_wiki_segment(self.message_id, self.segment_id)


class GetWikiPageMessage(Message):
    _required_fields = [
        'message_id',
        'page_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.get_wiki_page(self.message_id, self.page_id)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteWikiMessage(Message):
    _required_fields = [
        'message_id',
        'wiki_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def wiki_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_wiki(self.message_id, self.wiki_id)


class DeleteSegmentMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_segment(self.message_id, self.segment_id)


class DeleteTemplateHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'segment_id',
        'template_heading_title',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def segment_id(self) -> ObjectId: pass

    @auto_getattr
    def template_heading_title(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.delete_template_heading(self.message_id, self.segment_id, self.template_heading_title)


class DeletePageMessage(Message):
    _required_fields = [
        'message_id',
        'page_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_page(self.message_id, self.page_id)


class DeleteHeadingMessage(Message):
    _required_fields = [
        'message_id',
        'page_id',
        'heading_title',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    @auto_getattr
    def heading_title(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.delete_heading(self.message_id, self.heading_title, self.page_id)


class DeleteAliasMessage(Message):
    _required_fields = [
        'message_id',
        'alias_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def alias_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_alias(self.message_id, self.alias_id)
