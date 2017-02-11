from .LOMBase import LOMBase


class LOMHeading(LOMBase):
    @property
    def title(self) -> str:
        return self._body['title']

    @property
    def text(self) -> str:
        return self._body['text']
