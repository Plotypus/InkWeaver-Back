from .GenericHandler import GenericHandler


class SignUpHandler(GenericHandler):
    async def post(self):
        data = self.decode_json(self.request.body)
        username = data.get('username')
        password = data.get('password')
        name = data.get('name')
        email = data.get('email')
        bio = data.get('bio')
        if all([username, password, name, email, bio]):
            db_interface = self.settings['db_interface']
            try:
                await db_interface.create_user(username, password, name, email, bio)
                self.write_log('POST', self.request.uri, 200)
            except ValueError as e:
                message = e.args[0]
                # Username or email already exists
                self.write_log('POST', self.request.uri, 409)
                self.set_status(409)
                self.finish(message)
        else:
            self.write_log('POST', self.request.uri, 422)
            self.send_error(422)
