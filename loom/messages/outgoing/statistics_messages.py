from .outgoing_message import UnicastMessage


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics


class GetSectionStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics


class GetParagraphStatisticsOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics
