from .GenericHandler import GenericHandler

from tornado.escape import json_decode, json_encode


class BaseStoryHandler(GenericHandler):
    def write_json(self, dictionary):
        self.write(json_encode(dictionary))

    def success_write_json(self ,dictionary):
        dictionary['success'] = True
        self.write_json(dictionary)

    def post(self, *args, **kwargs):
        self.write(self.request.body)


class StoriesHandler(BaseStoryHandler):
    def get(self, user_id):
        self.success_write_json(dict(stories=list()))


class StoryHandler(BaseStoryHandler):
    def get(self, user_id, story_id):
        self.success_write_json(dict(story=story_id))


class ChapterHandler(BaseStoryHandler):
    def get(self, user_id, story_id, chapter_id):
        self.success_write_json(dict(story=story_id, chapter=chapter_id))


class ParagraphHandler(BaseStoryHandler):
    def get(self, user_id, story_id, chapter_id, paragraph_id):
        self.success_write_json(dict(story=story_id, chapter=chapter_id, paragraph=paragraph_id))
