from .GenericHandler import GenericHandler


class LoginHandler(GenericHandler):
    def post(self):
        data = self.decode_json(self.request.body)
        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            self.send_error(400)
            return
        db_interface = self.settings['db_interface']
        if db_interface.password_is_valid_for_username(username, password):
            # TODO: Generate session id and set the cookie
            pass
        else:
            self.send_error(401)  # Maybe 422?

