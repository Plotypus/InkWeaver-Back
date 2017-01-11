from .GenericHandler import GenericHandler


class LoginHandler(GenericHandler):
    async def post(self):
        data = self.decode_json(self.request.body)
        username = data.get('username')
        password = data.get('password')
        if username is not None and password is not None:
            db_interface = self.settings['db_interface']
            if await db_interface.password_is_valid_for_username(username, password):
                session_manager = self.settings['session_manager']
                session_id = session_manager.generate_session_id(username)
                self.set_secure_session_cookie(session_id)
            else:
                self.send_error(401)
        else:
            self.send_error(422)

    def set_secure_session_cookie(self, session_id):
        session_cookie_name = self.settings['session_cookie_name']
        # Have the cookie expire at the end of the session
        self.set_secure_cookie(session_cookie_name, session_id, None)

