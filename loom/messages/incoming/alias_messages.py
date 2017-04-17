from .incoming_message import IncomingMessage
from .field_types import RequiredField


###########################################################################
#
# Create Messages
#
###########################################################################
class CreateAliasIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.name = RequiredField()
        self.page_id = RequiredField()

    def dispatch(self):
        return self._dispatcher._create_alias(self.uuid, self.message_id, self.name, self.page_id)


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


###########################################################################
#
# Delete Messages
#
###########################################################################
class DeleteAliasIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.wiki_id = RequiredField()
        self.alias_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_alias(self.uuid, self.message_id, self.wiki_id, self.alias_id)
