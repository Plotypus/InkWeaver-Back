import loom.serialize as serialize

import tornado.web

class GenericHandler(tornado.web.RequestHandler):
    """
    The default Plotypus HTTP request handler.
    """
    def encode_json(self, data):
        return serialize.encode_bson_to_string(data)

    def decode_json(self, data):
        return serialize.decode_string_to_bson(data)

    def write_json(self, dictionary):
        self.write(self.encode_json(dictionary))

    def get(self, *args, **kwargs):
        self.send_error(405)

    def post(self, *args, **kwargs):
        self.send_error(405)

    def put(self, *args, **kwargs):
        self.send_error(405)

    def patch(self, *args, **kwargs):
        self.send_error(405)

    def delete(self, *args, **kwargs):
        self.send_error(405)
