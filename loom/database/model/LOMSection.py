from .LOMBase import LOMBase

from bson.objectid import ObjectId
from typing import List


class LOMParagraph(LOMBase):
    @property
    def _id(self) -> ObjectId:
        return self._body['_id']

    @property
    def text(self) -> str:
        return self._body['text']

    @property
    def statistics(self):
        return self._body['statistics']


class LOMLinkInfo(LOMBase):
    @property
    def paragraph_id(self) -> ObjectId:
        return self._body['paragraph_id']

    @property
    def links(self) -> List[ObjectId]:
        return self._body['links']


class LOMSection(LOMBase):
    def initialize(self):
        self._body['content'] = list(map(lambda p: LOMParagraph(p), self.content))

    @property
    def _id(self) -> ObjectId:
        return self._body['_id']
    
    @property
    def title(self) -> str:
        return self._body['title']
    
    @property
    def content(self) -> List[LOMParagraph]:
        return self._body['content']
    
    @property
    def preceding_subsections(self) -> List[ObjectId]:
        return self._body['preceding_subsections']
    
    @property
    def inner_subsections(self) -> List[ObjectId]:
        return self._body['inner_subsections']
    
    @property
    def succeeding_subsections(self) -> List[ObjectId]:
        return self._body['succeeding_subsections']
    
    @property
    def links(self) -> List[LOMLinkInfo]:
        return self._body['links']
    
    @property
    def statistics(self):
        return self._body['statistics']
