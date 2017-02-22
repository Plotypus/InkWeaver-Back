from .GenericHandler import GenericHandler

class EchoHandler(GenericHandler):
    async def post(self):
        print("Received POST: {}".format(self.request.body))
        self.write_json(self.request.body)

    async def get(self):
        print("Received GET")
        self.write_json("This is an echo server")
