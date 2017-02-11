from .LOMBase import LOMBase

from bson.objectid import ObjectId
from typing import List


class LOMAlias(LOMBase):
    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def name(self) -> str:
        return self._body['name']

    @property
    def page_id(self) -> ObjectId:
        return self._body['page_id']

    @property
    def links(self) -> List[ObjectId]:
        return self._body['links']