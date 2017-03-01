from .outgoing_message import OutgoingMessage


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryStatisticsOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics


class GetSectionStatisticsOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics


class GetParagraphStatisticsOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, statistics: dict):
        self.reply_to_id = reply_to_id
        self.statistics = statistics


class GetPageFrequenciesOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, pages: list):
        self.reply_to_id = reply_to_id
        self.pages = pages
