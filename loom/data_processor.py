from loom.database.interfaces import AbstractDBInterface
from loom.dispatchers import DemoDataDispatcher

class DataProcessor:
    def __init__(self, interface):
        self._interface = interface
        self._dispatcher = DemoDataDispatcher(self.interface)

    @property
    def interface(self) -> AbstractDBInterface:
        return self._interface
