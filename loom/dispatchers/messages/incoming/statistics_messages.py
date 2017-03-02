from .incoming_message import IncomingMessage


###########################################################################
#
# Get Messages
#
###########################################################################
class GetStoryStatisticsIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_story_statistics(self.message_id, self.story_id)


class GetSectionStatisticsIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_section_statistics(self.message_id, self.section_id)


class GetParagraphStatisticsIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'section_id',
        'paragraph_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_paragraph_statistics(self.message_id, self.section_id, self.paragraph_id)


class GetPageFrequenciesIncomingMessage(IncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
        'wiki_id',
    ]

    def dispatch(self):
        return self._dispatcher.get_page_frequencies(self.message_id, self.story_id, self.wiki_id)
