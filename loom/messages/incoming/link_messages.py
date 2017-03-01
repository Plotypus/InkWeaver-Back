from .incoming_message import IncomingMessage
from .field_types import RequiredField


###########################################################################
#
# Edit Messages
#
###########################################################################
class ChangeAliasNameIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.alias_id = RequiredField()
        self.new_name = RequiredField()

    def dispatch(self):
        return self._dispatcher.change_alias_name(self.message_id, self.alias_id, self.new_name)


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteLinkIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.link_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_link(self.message_id, self.link_id)
