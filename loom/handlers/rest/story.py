from .GenericHandler import GenericHandler

import loom.database


class StoriesHandler(GenericHandler):
    async def get(self):
        # TODO: Limit to current user
        self.write_json({
            'stories': list(),
        })

    async def post(self):
        try:
            story_id = await loom.database.create_story(**self.decode_json(self.request.body))
            self.write_json({
                'story_id': story_id,
            })
        except:
            # TODO: This should do validation in the event of incorrect fields or something.
            raise


class StoryHandler(GenericHandler):
    async def get(self, story_id):
        # TODO: Stitch chapters together
        self.write_json({
            'story': await loom.database.get_story(loom.database.hex_string_to_bson_oid(story_id)),
        })

    async def post(self):
        try:
            chapter_id = await loom.database.create_chapter(**self.decode_json(self.request.body))
            self.write_json({
                'chapter': chapter_id,
            })
        except:
            # TODO: This should do validation, too.
            raise


class ChapterHandler(GenericHandler):
    async def get(self, story_id, chapter_id):
        # TODO: Stitch paragraphs together
        chapter = await loom.database.get_chapter(loom.database.hex_string_to_bson_oid(chapter_id))
        self.write_json({
            'story':   story_id,
            'chapter': chapter,
        })


class ParagraphHandler(GenericHandler):
    def get(self, story_id, chapter_id, paragraph_id):
        self.write_json({
            'story':     story_id,
            'chapter':   chapter_id,
            'paragraph': paragraph_id,
        })
