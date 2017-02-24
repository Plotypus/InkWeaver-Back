from loom.loggers import connections
import loom.serialize as serialize

import tornado.web

class GenericHandler(tornado.web.RequestHandler):
    logger = connections

    def encode_json(self, data):
        return serialize.encode_bson_to_string(data)

    def decode_json(self, data):
        return serialize.decode_string_to_bson(data)

    def write_json(self, dictionary):
        self.write(self.encode_json(dictionary))

    def get(self, *args, **kwargs):
        error = 405
        self.logger.debug(f'GET {self.request.uri} -> {error}')
        self.send_error(error)

    def post(self, *args, **kwargs):
        error = 405
        self.logger.debug(f'POST {self.request.uri} -> {error}')
        self.send_error(error)

    def put(self, *args, **kwargs):
        error = 405
        self.logger.debug(f'PUT {self.request.uri} -> {error}')
        self.send_error(error)

    def patch(self, *args, **kwargs):
        error = 405
        self.logger.debug(f'PATCH {self.request.uri} -> {error}')
        self.send_error(error)

    def delete(self, *args, **kwargs):
        error = 405
        self.logger.debug(f'DELETE {self.request.uri} -> {error}')
        self.send_error(error)
