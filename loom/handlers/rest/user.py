from .GenericHandler import GenericHandler

import loom.database


class UsersHandler(GenericHandler):
    async def get(self):
        self.success_write_json(dict(users=await loom.database.get_all_user_ids()))

    async def post(self):
        try:
            user_id = await loom.database.create_user(**self.decode_json(self.request.body))
            self.success_write_json(dict(user_id=user_id))
        except:
            # TODO: This should probably do some things.
            raise
