from .LOMBase import LOMBase

from bson.objectid import ObjectId


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
