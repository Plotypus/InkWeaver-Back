from .LOMBase import LOMBase

from bson.objectid import ObjectId
from typing import List


class LOMUserDescription(LOMBase):
    @property
    def user_id(self) -> ObjectId:
        return self._body['user_id']

    @property
    def name(self) -> str:
        return self._body['name']

    @property
    def access_level(self) -> str:
        return self._body['access_level']


class LOMStory(LOMBase):
    def initialize(self):
        self._body['users'] = list(map(lambda u: LOMUserDescription(u), self.users))

    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def title(self) -> str:
        return self._body['title']

    @property
    def wiki_id(self) -> ObjectId:
        return self._body['wiki_id']

    @property
    def users(self) -> List[LOMUserDescription]:
        return self._body['users']

    @property
    def summary(self) -> str:
        return self._body['summary']

    @property
    def section_id(self) -> ObjectId:
        return self._body['section_id']

    @property
    def statistics(self):
        return self._body['statistics']

    @property
    def settings(self):
        return self._body['settings']
