from .base_router import BaseRouter

from loom.messages import WikiBroadcastMessage

from bson.objectid import ObjectId


class WikiRouter(BaseRouter):
    def broadcast(self, wiki_id: ObjectId, message: WikiBroadcastMessage):
        for handler in self.broadcast_map[wiki_id]:
            handler.write_json(message)
