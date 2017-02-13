from .message import Message, auto_getattr

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkMessage(Message):
    _required_fields = [
        'message_id',
        'story_id',
        'section_id',
        'paragraph_id',
        'name',
        'page_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def story_id(self) -> ObjectId: pass

    @auto_getattr
    def section_id(self) -> ObjectId: pass

    @auto_getattr
    def paragraph_id(self) -> ObjectId: pass

    @auto_getattr
    def name(self) -> str: pass

    @auto_getattr
    def page_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.create_link(self.message_id, self.story_id, self.section_id, self.paragraph_id, self.name,
                                     self.page_id)


###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameMessage(Message):
    _required_fields = [
        'message_id',
        'alias_id',
        'new_name',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def alias_id(self) -> ObjectId: pass

    @auto_getattr
    def new_name(self) -> str: pass

    def dispatch(self):
        return self._dispatcher.change_alias_name(self.message_id, self.alias_id, self.new_name)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkMessage(Message):
    _required_fields = [
        'message_id',
        'link_id',
    ]

    @auto_getattr
    def message_id(self) -> int: pass

    @auto_getattr
    def link_id(self) -> ObjectId: pass

    def dispatch(self):
        return self._dispatcher.delete_link(self.message_id, self.link_id)
