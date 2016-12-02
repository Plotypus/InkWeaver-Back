from . import LoomHandler

import loom.database

from tornado.ioloop import IOLoop


class TestHandler(LoomHandler):
    def open(self):
        super().open()
        IOLoop.current().spawn_callback(self.setup_user_session)

    async def setup_user_session(self):
        self.user = await loom.database.get_default_user()
        self.stories = {rand_id: story_id for (rand_id, story_id) in enumerate(self.user['stories'])}
        self.wikis = {rand_id: wiki_id for (rand_id, wiki_id) in enumerate(self.user['wikis'])}
