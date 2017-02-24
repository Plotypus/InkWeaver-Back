from .GenericHandler import GenericHandler
from .LoomHandler import LoomHandler

from loom.data_processor import DataProcessor
from loom.database.interfaces import MongoDBTornadoInterface
from loom.dispatchers import LAWProtocolDispatcher

from tornado.ioloop import IOLoop


class DemoHandler(LoomHandler):

    def initialize(self, demo_db_data):
        self.demo_db_data = demo_db_data

    def open(self):
        self.ready = False
        GenericHandler.open(self)
        self.db_name = '{}-{}'.format(self.settings['demo_db_prefix'], self.uuid)
        self.db_host = self.settings['demo_db_host']
        self.db_port = self.settings['demo_db_port']
        # TODO: Remove this.
        self.write_log('using DB: {}'.format(self.db_name))
        self._dispatcher = LAWProtocolDispatcher(self.db_interface)
        self.data_processor = DataProcessor(self.db_interface)
        self.startup()

    def on_close(self):
        IOLoop.current().spawn_callback(self.teardown)
        super().on_close()

    def startup(self):
        IOLoop.current().spawn_callback(self.load_file_and_set_user, self.demo_db_data)
        self.initialize_queue()

    async def teardown(self):
        await self.db_interface.drop_database()
        self.write_log("dropped database: {}".format(self.db_name))

    async def load_file_and_set_user(self, filename):
        user_id = await self.data_processor.load_file(filename)
        self.dispatcher.set_user_id(user_id)
        self.write_log("generated database from file: {}".format(self.demo_db_data))
        self.ready = True
        self.send_ready_acknowledgement()

    @property
    def db_interface(self):
        try:
            return self._db_interface
        except AttributeError:
            self._db_interface = MongoDBTornadoInterface(self.db_name, self.db_host, self.db_port)
            return self._db_interface
