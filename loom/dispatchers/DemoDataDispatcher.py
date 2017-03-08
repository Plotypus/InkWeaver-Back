from loom.dispatchers.LAWProtocolDispatcher import LAWProtocolDispatcher
from loom.messages.outgoing.demo import AddTextToSectionOutgoingMessage


class DemoDataDispatcher(LAWProtocolDispatcher):
    def __init__(self, interface):
        super().__init__(interface)

    async def add_heading_with_text(self, uuid, message_id, title, text, page_id):
        # Don't care about the return contents, just force execution
        async for _ in super().add_heading(uuid, message_id, title, page_id):
            continue
        update = {
            'update_type': 'set_text',
            'text': text,
        }
        # Don't care about the return contents, just force execution
        async for _ in super().edit_heading(uuid, message_id, page_id, title, update):
            continue
        # Async equivalent to `return None`
        return
        yield

    async def add_text_to_section(self, uuid, message_id, text, section_id):
        paragraphs = text.split('\n\n')
        for paragraph in paragraphs:
            # Don't care about the return contents, just force execution
            async for _ in super().add_paragraph(uuid, message_id, section_id, paragraph):
                continue
        # Async equivalent to `return None`
        return
        yield
