from .GenericHandler import GenericHandler

from loom.database.interfaces import AbstractDBInterface

class LoginHandler(GenericHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', 'http://localhost:3000')
        self.set_header('Access-Control-Allow-Credentials', 'true')

    async def post(self):
        data = self.decode_json(self.request.body)
        username = data.get('username')
        password = data.get('password')
        if username is not None and password is not None:
            db_interface = self.settings['db_interface']
            if await db_interface.password_is_valid_for_username(username, password):
                user_id = await self._get_user_id_for_username(username)
                session_manager = self.settings['session_manager']
                session_id = session_manager.generate_session_id_for_user(user_id)
                self.set_secure_session_cookie(session_id)
            else:
                self.send_error(401)
        else:
            self.send_error(422)

    async def _get_user_id_for_username(self, username):
        db_interface: AbstractDBInterface = self.settings['db_interface']
        user_id = await db_interface.get_user_id_for_username(username)
        return user_id

    def set_secure_session_cookie(self, session_id):
        session_cookie_name = self.settings['session_cookie_name']
        # Have the cookie expire at the end of the session
        self.set_secure_cookie(session_cookie_name, session_id, None)

