from .incoming_message import SubscriptionIncomingMessage


###########################################################################
#
# Story Messages
#
###########################################################################
class SubscribeToStoryIncomingMessage(SubscriptionIncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]


class UnsubscribeFromStoryIncomingMessage(SubscriptionIncomingMessage):
    _required_fields = [
        'message_id',
    ]


###########################################################################
#
# Wiki Messages
#
###########################################################################
class SubscribeToWikiIncomingMessage(SubscriptionIncomingMessage):
    _required_fields = [
        'message_id',
        'story_id',
    ]


class UnsubscribeFromWikiIncomingMessage(SubscriptionIncomingMessage):
    _required_fields = [
        'message_id',
    ]
