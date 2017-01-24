from .GenericHandler import GenericHandler
from .LoomHandler import LoomHandler

from loom.database.interfaces import MongoDBTornadoInterface
from loom.dispatchers import LAWProtocolDispatcher

class DemoHandler(LoomHandler):

    def open(self):
        GenericHandler.open(self)
        self.db_name = 'demo-db-{}'.format(self.uuid)
        self.db_host = self.settings['demo_db_host']
        self.db_port = self.settings['demo_db_port']
        # TODO: Remove this.
        self.write_console_message('using DB: {}'.format(self.db_name))
        self._dispatcher = LAWProtocolDispatcher(self.db_interface)

    @property
    def db_interface(self):
        try:
            return self._db_interface
        except AttributeError:
            self._db_interface = MongoDBTornadoInterface(self.db_name, self.db_host, self.db_port)
            return self._db_interface
