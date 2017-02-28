from loom.messages import BroadcastMessage
from loom.handlers.websockets.LoomHandler import LoomHandler

from abc import ABC, abstractmethod
from bson.objectid import ObjectId
from collections import defaultdict

from typing import DefaultDict, Set


class BaseRouter(ABC):
    def __init__(self):
        self.broadcast_map: DefaultDict[ObjectId, Set[LoomHandler]] = defaultdict(set)

    def subscribe(self, object_id: ObjectId, handler: LoomHandler):
        self.broadcast_map[object_id].add(handler)

    def unsubscribe(self, object_id: ObjectId, handler: LoomHandler):
        self.broadcast_map[object_id].remove(handler)

    @abstractmethod
    def broadcast(self, object_id: ObjectId, message: BroadcastMessage):
        pass
