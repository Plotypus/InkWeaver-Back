from .GenericHandler import GenericHandler

import loom.database


class StoriesHandler(GenericHandler):
    async def get(self):
        # TODO: Limit to current user
        self.success_write_json(dict(stories=list()))

    async def post(self):
        story_id = await loom.database.create_story(**self.decode_json(self.request.body))
        self.success_write_json(dict(story_id=story_id))


class StoryHandler(GenericHandler):
    async def get(self, story_id):
        # TODO: Stitch chapters together
        self.success_write_json(dict(story=await loom.database.get_story(story_id)))

    async def post(self):
        chapter_id = await loom.database.create_chapter(**self.decode_json(self.request.body))
        self.success_write_json(dict(chapter=chapter_id))


class ChapterHandler(GenericHandler):
    async def get(self, story_id, chapter_id):
        # TODO: Stitch paragraphs together
        chapter = await loom.database.get_chapter(chapter_id)
        self.success_write_json(dict(story=story_id, chapter=chapter))


class ParagraphHandler(GenericHandler):
    def get(self, story_id, chapter_id, paragraph_id):
        self.success_write_json(dict(story=story_id, chapter=chapter_id, paragraph=paragraph_id))
