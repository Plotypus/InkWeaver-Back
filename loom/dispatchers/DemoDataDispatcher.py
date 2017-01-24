from .LAWProtocolDispatcher import LAWProtocolDispatcher


class DemoDataDispatcher(LAWProtocolDispatcher):
    def __init__(self, interface):
        super().__init__(interface)
        self.approved += [
            'create_user',
        ]

    async def create_user(self, message_id, username, password, email):
        user_id = await self.db_interface.create_user(username, password, email)
        self.set_user_id(user_id)
