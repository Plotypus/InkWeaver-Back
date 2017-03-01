from .outgoing_message import UnicastMessage

from uuid import UUID


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, statistics: dict):
        super().__init__(uuid, message_id, 'got_story_statistics')
        self.statistics = statistics


class GetSectionStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, statistics: dict):
        super().__init__(uuid, message_id, 'got_section_statistics')
        self.statistics = statistics


class GetParagraphStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, statistics: dict):
        super().__init__(uuid, message_id, 'got_paragraph_statistics')
        self.statistics = statistics
