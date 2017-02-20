from .LOMBase import LOMBase
from .LOMContext import LOMContext

from bson.objectid import ObjectId


class LOMLink(LOMBase):
    @property
    def id(self) -> ObjectId:
        return self._body['_id']

    @property
    def context(self) -> LOMContext:
        return self._body['context']

    @property
    def alias_id(self) -> ObjectId:
        return self._body['alias_id']

    @property
    def page_id(self) -> ObjectId:
        return self._body['page_id']
