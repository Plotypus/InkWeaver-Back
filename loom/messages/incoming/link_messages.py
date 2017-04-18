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
        self.story_id = RequiredField()
        self.wiki_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.approve_passive_link(self.uuid, self.message_id, self.passive_link_id, self.story_id,
                                                     self.wiki_id)


class RejectPassiveLinkMessage(IncomingMessage):
    def __init__(self):
        super().__init__()
        self.passive_link_id = RequiredField()

    def dispatch(self):
        return self._dispatcher.reject_passive_link(self.uuid, self.message_id, self.passive_link_id)


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
