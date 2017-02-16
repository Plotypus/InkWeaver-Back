from .LOMBase import LOMBase

from bson.objectid import ObjectId


class LOMContext(LOMBase):
    @property
    def story_id(self) -> ObjectId:
        return self._body['story_id']

    @property
    def section_id(self) -> ObjectId:
        return self._body['section_id']

    @property
    def paragraph_id(self) -> ObjectId:
        return self._body['paragraph_id']

    @property
    def text(self) -> str:
        return self._body['text']
