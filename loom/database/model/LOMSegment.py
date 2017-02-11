from .LOMBase import LOMBase
from .LOMHeading import LOMHeading

from bson.objectid import ObjectId
from typing import List


class LOMSegment(LOMBase):
    def initialize(self):
        self._body['template_headings'] = list(map(lambda h: LOMHeading(h), self._body['template_headings']))

    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def title(self) -> str:
        return self._body['title']

    @property
    def segments(self) -> List[ObjectId]:
        return self._body['segments']

    @property
    def pages(self) -> List[ObjectId]:
        return self._body['pages']

    @property
    def template_headings(self) -> List[LOMHeading]:
        return self._body['template_headings']

    @property
    def statistics(self):
        return self._body['statistics']
