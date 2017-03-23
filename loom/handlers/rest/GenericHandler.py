from loom.loggers import rest_connections
import loom.serialize as serialize

import tornado.web

class GenericHandler(tornado.web.RequestHandler):
    logger = rest_connections

    def set_default_headers(self):
        login_origin = self.settings['login_origin']
        self.set_header('Access-Control-Allow-Origin', login_origin)
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Headers', 'content-type')

    async def options(self):
        self.write_log('OPTIONS', self.request.uri, 204)
        self.set_status(204)
        self.finish()

    def encode_json(self, data):
        return serialize.encode_bson_to_string(data)

    def decode_json(self, data):
        return serialize.decode_string_to_bson(data)

    def write_json(self, dictionary):
        self.write(self.encode_json(dictionary))

    def write_log(self, method, url, response, extra=None):
        message = f'{method} {url} -> {response}'
        if extra is not None:
            message = f'{message} {extra}'
        self.logger.info(message)

    def get(self, *args, **kwargs):
        error = 405
        self.write_log('GET', self.request.uri, error)
        self.send_error(error)

    def post(self, *args, **kwargs):
        error = 405
        self.write_log('POST', self.request.uri, error)
        self.send_error(error)

    def put(self, *args, **kwargs):
        error = 405
        self.write_log('PUT', self.request.uri, error)
        self.send_error(error)

    def patch(self, *args, **kwargs):
        error = 405
        self.write_log('PATCH', self.request.uri, error)
        self.send_error(error)

    def delete(self, *args, **kwargs):
        error = 405
        self.write_log('DELETE', self.request.uri, error)
        self.send_error(error)
