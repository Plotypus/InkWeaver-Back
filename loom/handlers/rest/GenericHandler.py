import tornado.web

from tornado.escape import json_decode, json_encode

class GenericHandler(tornado.web.RequestHandler):
    """
    The default Plotypus HTTP request handler.
    """
    def encode_json(self, data):
        return json_encode(data)

    def decode_json(self, data):
        return json_decode(data)

    def write_json(self, dictionary):
        self.write(self.encode_json(dictionary))

    def success_write_json(self ,dictionary):
        dictionary['success'] = True
        self.write_json(dictionary)

    def post(self, *args, **kwargs):
        self.write(self.request.body)
