from loom.messages import BroadcastMessage, UnicastMessage, StoryBroadcastMessage, WikiBroadcastMessage
from loom.handlers.websockets.LoomHandler import LoomHandler

from bson.objectid import ObjectId
from collections import defaultdict
from uuid import UUID

from typing import Dict, Set


class Router:
    def __init__(self):
        self.broadcast_map: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.lookup_map: Dict[UUID, ObjectId] = dict()
        self.handler_map: Dict[UUID, LoomHandler] = dict()

    def subscribe(self, object_id: ObjectId, handler: LoomHandler):
        uuid = handler.uuid
        self.handler_map[uuid] = handler
        self.lookup_map[uuid] = object_id
        self.broadcast_map[object_id].add(uuid)

    def unsubscribe(self, object_id: ObjectId, handler: LoomHandler):
        uuid = handler.uuid
        self._unsubscribe(object_id, uuid)

    def _unsubscribe(self, object_id: ObjectId, uuid: UUID):
        self.broadcast_map[object_id].remove(uuid)
        del(self.lookup_map[uuid])

    def remove(self, handler: LoomHandler):
        uuid = handler.uuid
        object_id = self.lookup_map[uuid]
        self._unsubscribe(object_id, uuid)
        del(self.handler_map[uuid])

    def unicast(self, message: UnicastMessage):
        uuid = message.identifier.uuid
        handler = self.handler_map[uuid]
        handler.write_json(message)

    def broadcast(self, object_id: ObjectId, message: BroadcastMessage):
        for uuid in self.broadcast_map[object_id]:
            handler = self.handler_map[uuid]
            handler.write_json(message)


class StoryRouter(Router):
    def broadcast(self, object_id: ObjectId, message: StoryBroadcastMessage):
        super().broadcast(object_id, message)


class WikiRouter(Router):
    def broadcast(self, object_id: ObjectId, message: WikiBroadcastMessage):
        super().broadcast(object_id, message)
