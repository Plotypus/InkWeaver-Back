from .incoming_message import IncomingMessage
from ..message import auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWikiIncomingMessage(IncomingMessage):
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
class AddSegmentIncomingMessage(IncomingMessage):
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


class AddTemplateHeadingIncomingMessage(IncomingMessage):
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


class AddPageIncomingMessage(IncomingMessage):
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


class AddHeadingIncomingMessage(IncomingMessage):
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
class EditSegmentIncomingMessage(IncomingMessage):
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


class EditTemplateHeadingIncomingMessage(IncomingMessage):
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


class EditPageIncomingMessage(IncomingMessage):
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


class EditHeadingIncomingMessage(IncomingMessage):
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
class GetWikiInformationIncomingMessage(IncomingMessage):
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


class GetWikiHierarchyIncomingMessage(IncomingMessage):
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


class GetWikiSegmentHierarchyIncomingMessage(IncomingMessage):
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


class GetWikiSegmentIncomingMessage(IncomingMessage):
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


class GetWikiPageIncomingMessage(IncomingMessage):
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
class DeleteWikiIncomingMessage(IncomingMessage):
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


class DeleteSegmentIncomingMessage(IncomingMessage):
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


class DeleteTemplateHeadingIncomingMessage(IncomingMessage):
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


class DeletePageIncomingMessage(IncomingMessage):
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


class DeleteHeadingIncomingMessage(IncomingMessage):
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


class DeleteAliasIncomingMessage(IncomingMessage):
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
