from .incoming_message import IncomingMessage
from .field_types import RequiredField


###########################################################################
#
# Approve Passive Link Messages
#
###########################################################################
class ApprovePassiveLinkMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.passive_link_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.approve_passive_link(self.uuid, self.message_id, self.passive_link_id)


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
class DeleteLinkIncomingMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.link_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.delete_link(self.uuid, self.message_id, self.link_id)
