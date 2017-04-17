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
        self.wiki_id = RequiredField()
        self.alias_id = RequiredField()
        self.new_name = RequiredField()

    def dispatch(self):
        return self._dispatcher.change_alias_name(self.uuid, self.message_id, self.wiki_id,  self.alias_id,
                                                  self.new_name)