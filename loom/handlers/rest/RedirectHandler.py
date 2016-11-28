from .GenericHandler import GenericHandler

class RedirectHandler(GenericHandler):
    def initialize(self, url, permanent=False, status=None):
        self.url = url
        self.permanent = permanent
        self.status = status

    def get(self):
        self.redirect(url=self.url, permanent=self.permanent, status=self.status)
