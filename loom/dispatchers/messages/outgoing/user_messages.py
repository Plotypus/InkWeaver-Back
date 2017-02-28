from .outgoing_message import UnicastMessage


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, username: str, name: str, email: str, bio: str, avatar: str):
        self.reply_to_id = reply_to_id
        self.username = username
        self.name = name
        self.email = email
        self.bio = bio
        self.avatar = avatar

    
class GetUserStoriesOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, stories: list):
        self.reply_to_id = reply_to_id
        self.stories = stories

    
class GetUserWikisOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, wikis: list):
        self.reply_to_id = reply_to_id
        self.wikis = wikis


###########################################################################
#
# Set Messages
#
###########################################################################
class SetUserNameOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


class SetUserEmailOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


class SetUserBioOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int):
        self.reply_to_id = reply_to_id


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginOutgoingMessage(UnicastMessage):
    def __init__(self, reply_to_id: int, event: str):
        self.reply_to_id = reply_to_id
        self.event = event
