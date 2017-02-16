from .outgoing_message import OutgoingMessage
from ..message import auto_getattr


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, username: str, name: str, email: str, bio: str, avatar: str):
        self.reply_to_id = reply_to_id
        self.username = username
        self.name = name
        self.email = email
        self.bio = bio
        self.avatar = avatar

    
class GetUserStoriesOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, stories: list):
        self.reply_to_id = reply_to_id
        self.stories = stories

    
class GetUserWikisOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, wikis: list):
        self.reply_to_id = reply_to_id
        self.wikis = wikis


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginOutgoingMessage(OutgoingMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
