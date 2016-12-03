from . import LoomHandler

import loom.database

from tornado.ioloop import IOLoop


class TestHandler(LoomHandler):
    def open(self):
        super().open()
        IOLoop.current().spawn_callback(self.setup_user_session)

    async def setup_user_session(self):
        # TODO: For stories and wikis, get the titles as well
        self.user = await loom.database.get_default_user()
        setup_stories_future = super()._create_story_ids_mapping()
        setup_wikis_future = super()._create_wiki_ids_mapping()
        await setup_stories_future
        await setup_wikis_future
