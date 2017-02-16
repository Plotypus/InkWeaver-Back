from .LOMBase import LOMBase

from bson.objectid import ObjectId
from typing import List


class LOMUser(LOMBase):
    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def username(self) -> str:
        return self._body['username']

    @property
    def password_hash(self) -> str:
        return self._body['password_hash']

    @property
    def name(self) -> str:
        return self._body['name']

    @property
    def email(self) -> str:
        return self._body['email']

    @property
    def stories(self) -> List[ObjectId]:
        return self._body['stories']

    @property
    def wikis(self) -> List[ObjectId]:
        return self._body['wikis']

    @property
    def avatar(self):
        return self._body['avatar']

    @property
    def bio(self) -> str:
        return self._body['bio']

    @property
    def statistics(self):
        return self._body['statistics']
