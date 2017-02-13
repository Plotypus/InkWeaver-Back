from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateWiki(Message):
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
        self._dispatcher.create_wiki(self.message_id, self.title, self.summary)


###########################################################################
#
# Add Messages
#
###########################################################################
class AddSegment(Message):
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
        self._dispatcher.add_segment(self.message_id, self.title, self.parent_id)


class AddTemplateHeading(Message):
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
        self._dispatcher.add_template_heading(self.message_id, self.title, self.segment_id)


class AddPage(Message):
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
        self._dispatcher.add_page(self.message_id, self.title, self.parent_id)


class AddHeading(Message):
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
        self._dispatcher.add_heading(self.message_id, self.title, self.page_id, self.index)


###########################################################################
#
# Edit Messages
#
###########################################################################
class EditSegment(Message):
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
        self._dispatcher.edit_segment(self.message_id, self.segment_id, self.update)


class EditTemplateHeading(Message):
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
        self._dispatcher.edit_template_heading(self.message_id, self.segment_id, self.template_heading_title,
                                               self.update)


class EditPage(Message):
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
        self._dispatcher.edit_page(self.message_id, self.page_id, self.update)


class EditHeading(Message):
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
        self._dispatcher.edit_heading(self.message_id, self.page_id, self.heading_title, self.update)
