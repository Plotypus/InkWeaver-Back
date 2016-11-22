from .GenericHandler import GenericHandler

import loom.database


class UsersHandler(GenericHandler):
    async def get(self):
        # TODO: Remove this.
        self.write_json({
            'users': await loom.database.get_all_user_ids(),
        })

    async def post(self):
        try:
            user_id = await loom.database.create_user(**self.decode_json(self.request.body))
            self.write_json({
                'user_id': user_id,
            })
        except:
            # TODO: Validate contents of body and report error accordingly.
            raise
