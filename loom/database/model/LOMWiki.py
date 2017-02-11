from .LOMBase import LOMBase
from .LOMUserDescription import LOMUserDescription

from bson.objectid import ObjectId
from typing import List


class LOMWiki(LOMBase):
    def initialize(self):
        self._body['users'] = list(map(lambda u: LOMUserDescription(u), self._body['users']))

    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def title(self) -> str:
        return self._body['title']

    @property
    def users(self) -> List[LOMUserDescription]:
        return self._body['users']

    @property
    def summary(self) -> str:
        return self._body['summary']

    @property
    def segment_id(self) -> ObjectId:
        return self._body['segment_id']

    @property
    def statistics(self):
        return self._body['statistics']

    @property
    def settings(self):
        return self._body['settings']
