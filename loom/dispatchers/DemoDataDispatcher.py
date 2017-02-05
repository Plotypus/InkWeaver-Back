from .LAWProtocolDispatcher import LAWProtocolDispatcher


class DemoDataDispatcher(LAWProtocolDispatcher):
    def __init__(self, interface):
        super().__init__(interface)
        self.approved += [
            'create_user',
            'add_heading_with_text',
            'add_text_to_section',
        ]

    async def create_user(self, message_id, username, password, email):
        user_id = await self.db_interface.create_user(username, password, email)
        self.set_user_id(user_id)

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
