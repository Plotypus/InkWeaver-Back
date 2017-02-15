from .demo_message_factory import DemoIncomingMessageFactory

from loom.dispatchers.LAWProtocolDispatcher import LAWProtocolDispatcher


class DemoDataDispatcher(LAWProtocolDispatcher):
    def __init__(self, interface):
        super().__init__(interface)
        self._message_factory = DemoIncomingMessageFactory()

    async def add_heading_with_text(self, message_id, title, text, page_id):
        await super().add_heading(message_id, title, page_id)
        update = {
            'update_type': 'set_text',
            'text': text,
        }
        await super().edit_heading(message_id, page_id, title, update)

    async def add_text_to_section(self, message_id, text, section_id):
        paragraphs = text.split('\n\n')
        paragraph_ids = {}
        for paragraph in paragraphs:
            paragraph_id = (await super().add_paragraph(message_id, section_id, paragraph))['paragraph_id']
            paragraph_ids[str(len(paragraph_ids))] = paragraph_id
        return self.format_json({'paragraph_ids': paragraph_ids})
