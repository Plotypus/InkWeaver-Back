from .outgoing_message import UnicastMessage

from uuid import UUID


###########################################################################
#
# Get Messages
#
###########################################################################
class GetUserPreferencesOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, username: str, name: str, email: str, bio: str, avatar: str):
        super().__init__(uuid, message_id, 'got_user_preferences')
        self.username = username
        self.name = name
        self.email = email
        self.bio = bio
        self.avatar = avatar


class GetUserStoriesAndWikisOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int, *, stories: list, wikis: list):
        super().__init__(uuid, message_id, 'got_user_stories_and_wikis')
        self.stories = stories
        self.wikis = wikis


###########################################################################
#
# Set Messages
#
###########################################################################
class SetUserNameOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'user_name_updated')


class SetUserEmailOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'user_email_updated')


class SetUserBioOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'user_bio_updated')


###########################################################################
#
# Login Messages
#
###########################################################################
class UserLoginOutgoingMessage(UnicastMessage):
    def __init__(self, uuid: UUID, message_id: int):
        super().__init__(uuid, message_id, 'logged_in')