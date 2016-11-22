from .GenericHandler import GenericHandler


class StoriesHandler(GenericHandler):
    def get(self, user_id):
        self.success_write_json(dict(stories=list()))


class StoryHandler(GenericHandler):
    def get(self, user_id, story_id):
        self.success_write_json(dict(story=story_id))


class ChapterHandler(GenericHandler):
    def get(self, user_id, story_id, chapter_id):
        self.success_write_json(dict(story=story_id, chapter=chapter_id))


class ParagraphHandler(GenericHandler):
    def get(self, user_id, story_id, chapter_id, paragraph_id):
        self.success_write_json(dict(story=story_id, chapter=chapter_id, paragraph=paragraph_id))
