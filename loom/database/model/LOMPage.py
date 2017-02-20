from .LOMBase import LOMBase
from .LOMContext import LOMContext
from .LOMHeading import LOMHeading

from bson.objectid import ObjectId
from typing import Dict, List


class LOMReference(LOMBase):
    def initialize(self):
        self._body['context'] = LOMContext(self._body['context'])

    @property
    def link_id(self) -> ObjectId:
        return self._body['link_id']

    @property
    def context(self) -> LOMContext:
        return self._body['context']


class LOMPage(LOMBase):
    def initialize(self):
        self._body['headings'] = list(map(lambda h: LOMHeading(h), self._body['headings']))
        self._body['references'] = list(map(lambda r: LOMReference(r), self._body['references']))

    @property
    def id(self) -> ObjectId:
        return self._body['_id']

    @property
    def title(self) -> str:
        return self._body['title']

    @property
    def headings(self) -> List[LOMHeading]:
        return self._body['headings']

    @property
    def references(self) -> List[LOMReference]:
        return self._body['references']

    @property
    def aliases(self) -> Dict[str, ObjectId]:
        return self._body['aliases']
