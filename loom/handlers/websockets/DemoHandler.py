from .GenericHandler import GenericHandler
from .LoomHandler import LoomHandler

from loom.database.interfaces import MongoDBTornadoInterface

class DemoHandler(LoomHandler):

    def open(self):
        GenericHandler.open(self)
        db_name = 'demo-db-{}'.format(self.uuid)
        db_host = self.settings['demo_db_host']
        db_port = self.settings['demo_db_port']
        self._db_interface = MongoDBTornadoInterface(db_name, db_host, db_port)
        # TODO: Remove this.
        self.write_console_message('using DB: {}'.format(db_name))

    @property
    def db_interface(self):
        return self._db_interface
