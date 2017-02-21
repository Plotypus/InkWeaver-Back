from .incoming_message import IncomingMessage

from bson import ObjectId


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateLinkIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
        'section_id',
        'paragraph_id',
        'name',
        'page_id',
    ]

    def dispatch(self):
        return self._dispatcher.create_link(self.message_id, self.story_id, self.section_id, self.paragraph_id,
                                            self.name, self.page_id)


###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'alias_id',
        'new_name',
    ]

    def dispatch(self):
        return self._dispatcher.change_alias_name(self.message_id, self.alias_id, self.new_name)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'link_id',
    ]

    def dispatch(self):
        return self._dispatcher.delete_link(self.message_id, self.link_id)
