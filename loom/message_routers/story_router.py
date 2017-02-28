from .base_router import BaseRouter

from loom.messages import StoryBroadcastMessage

from bson.objectid import ObjectId


class StoryRouter(BaseRouter):
    def broadcast(self, story_id: ObjectId, message: StoryBroadcastMessage):
        for handler in self.broadcast_map[story_id]:
            handler.write_json(message)
