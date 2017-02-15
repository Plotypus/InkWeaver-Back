from .outgoing_message import OutgoingMessage
from ..message import auto_getattr


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'username',
        'name',
        'email',
        'bio',
        'avatar',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def username(self) -> str: pass

    @auto_getattr
    def name(self) -> str: pass

    @auto_getattr
    def email(self) -> str: pass

    @auto_getattr
    def bio(self) -> str: pass

    @auto_getattr
    def avatar(self) -> str: pass

    
class GetUserStoriesOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'stories',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def stories(self) -> list: pass

    
class GetUserWikisOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'wikis',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def wikis(self) -> list: pass


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginOutgoingMessage(OutgoingMessage):
    _required_fields = [
        'reply_to_id',
        'event',
    ]

    @auto_getattr
    def reply_to_id(self) -> int: pass

    @auto_getattr
    def event(self) -> str: pass
