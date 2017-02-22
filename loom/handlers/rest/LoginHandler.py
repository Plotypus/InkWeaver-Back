from .GenericHandler import GenericHandler

from loom.database.interfaces import AbstractDBInterface

class LoginHandler(GenericHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', 'https://inkweaver.plotypus.net')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers', 'content-type')

    async def options(self):
        self.set_status(204)
        self.finish()

    async def post(self):
        cookie = self._get_secure_session_cookie()
        if cookie is not None:
            session_id = cookie.decode('UTF-8')
            print(f"SESSION_ID: {session_id}")
        else:
            print(f"SESSION COOKIE WAS NOT SET")

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

    def _get_secure_session_cookie(self):
        cookie_name = self.settings['session_cookie_name']
        # Make sure users cannot use cookies for more than their session
        cookie = self.get_secure_cookie(cookie_name, max_age_days=0.5)
        # Cookies are retrieved as a byte-string, we need to decode it.
        return cookie
        # decoded_cookie = cookie.decode('UTF-8')
        # return decoded_cookie

    async def _get_user_id_for_username(self, username):
        db_interface: AbstractDBInterface = self.settings['db_interface']
        user_id = await db_interface.get_user_id_for_username(username)
        return user_id

    def set_secure_session_cookie(self, session_id):
        session_cookie_name = self.settings['session_cookie_name']
        # Have the cookie expire at the end of the session
        self.set_secure_cookie(session_cookie_name, session_id, None)

