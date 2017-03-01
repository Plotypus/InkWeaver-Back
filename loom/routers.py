from loom.dispatchers import LAWProtocolDispatcher
from loom.handlers.websockets.LoomHandler import LoomHandler
from loom.messages.incoming import (
    IncomingMessage, IncomingMessageFactory, SubscriptionIncomingMessage,
    SubscribeToStoryIncomingMessage, SubscribeToWikiIncomingMessage,
    UnsubscribeFromStoryIncomingMessage, UnsubscribeFromWikiIncomingMessage,
)
from loom.messages.outgoing import (
    BroadcastMessage, UnicastMessage, StoryBroadcastMessage, WikiBroadcastMessage, OutgoingErrorMessage,
    SubscribeToStoryOutgoingMessage, SubscribeToWikiOutgoingMessage,
    UnsubscribeFromStoryOutgoingMessage, UnsubscribeFromWikiOutgoingMessage
)

from bson.objectid import ObjectId
from collections import defaultdict
from uuid import UUID

from typing import Dict, Set
JSON = Dict


class Router:
    def __init__(self, interface):
        # Classes used throughout.
        self.dispatcher = LAWProtocolDispatcher(interface)
        self.message_factory = IncomingMessageFactory()
        # Various dictionaries for keeping track of user information.
        self.story_to_users: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.wiki_to_users: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.user_to_story: Dict[UUID, ObjectId] = dict()
        self.user_to_wiki: Dict[UUID, ObjectId] = dict()
        self.user_to_handler: Dict[UUID, LoomHandler] = dict()

    def process_incoming(self, handler: LoomHandler, message: JSON, action: str, message_id=None):
        # Receive the message and format it into one of our IncomingMessage objects.
        try:
            message_object: IncomingMessage = self.message_factory.build_message(self, action, message)
        # Bad action.
        except ValueError:
            return self.dispatcher.format_failure_json(message_id, f"Action '{action}' not supported.")
        # Bad message format.
        except TypeError as e:
            # TODO: Replace with with a more specific error
            message = e.args[0]
            return self.dispatcher.format_failure_json(message_id, message)
        # Check whether the user is already connected to the router.
        uuid = handler.uuid
        if uuid not in self.user_to_handler:
            self.user_to_handler[uuid] = handler
        # Check if the new message is meant for subscription.
        if isinstance(message, SubscriptionIncomingMessage):
            if isinstance(message, SubscribeToStoryIncomingMessage):
                self.subscribe_to_story(message.story_id, uuid, message_id)
            elif isinstance(message, SubscribeToWikiIncomingMessage):
                self.subscribe_to_wiki(message.wiki_id, uuid, message_id)
            elif isinstance(message, UnsubscribeFromStoryIncomingMessage):
                self.unsubscribe_from_story(uuid, message_id)
            elif isinstance(message, UnsubscribeFromWikiIncomingMessage):
                self.unsubscribe_from_wiki(uuid, message_id)
            else:
                raise RuntimeError("unknown instance of SubscriptionIncomingMessage")
        else:
            self.dispatcher.dispatch(message_object, action, message_id)

    def disconnect(self, handler: LoomHandler):
        uuid = handler.uuid
        self._unsubscribe_from_story(uuid)
        self._unsubscribe_from_wiki(uuid)
        del(self.user_to_handler[uuid])

    def subscribe_to_story(self, story_id: ObjectId, uuid: UUID, message_id: int):
        if uuid in self.user_to_story:
            # The user is already subscribed to another story.
            err_msg = OutgoingErrorMessage(message_id, "Cannot subscribe to multiple stories.")
            self.unicast(err_msg)
        else:
            self.story_to_users[story_id].add(uuid)
            self.user_to_story[uuid] = story_id
            response = SubscribeToStoryOutgoingMessage(message_id, 'subscribed_to_story')
            self.unicast(response)

    def subscribe_to_wiki(self, wiki_id: ObjectId, uuid: UUID, message_id: int):
        if uuid in self.user_to_wiki:
            # The user is already subscribed to another wiki.
            err_msg = OutgoingErrorMessage(message_id, "Cannot subscribe to multiple wikis.")
            self.unicast(err_msg)
        else:
            self.wiki_to_users[wiki_id].add(uuid)
            self.user_to_wiki[uuid] = wiki_id
            response = SubscribeToWikiOutgoingMessage(message_id, 'subscribed_to_wiki')
            self.unicast(response)

    def unsubscribe_from_story(self, uuid: UUID, message_id: int):
        if uuid not in self.user_to_story:
            # The user is not currently subscribed to any story.
            err_msg = OutgoingErrorMessage(message_id, "Cannot unsubscribe from story; no active story subscription.")
            self.unicast(err_msg)
        else:
            self._unsubscribe_from_story(uuid)
            response = UnsubscribeFromStoryOutgoingMessage(message_id, 'unsubscribed_from_story')
            self.unicast(response)

    def _unsubscribe_from_story(self, uuid: UUID):
            story_id = self.user_to_story[uuid]
            self.story_to_users[story_id].remove(uuid)
            del(self.user_to_story[uuid])

    def unsubscribe_from_wiki(self, uuid: UUID, message_id: int):
        if uuid not in self.user_to_wiki:
            # The user is not currently subscribed to any wiki.
            err_msg = OutgoingErrorMessage(message_id, "Cannot unsubscribe from wiki; no active wiki subscription.")
            self.unicast(err_msg)
        else:
            self._unsubscribe_from_wiki(uuid)
            response = UnsubscribeFromWikiOutgoingMessage(message_id, 'unsubscribed_from_wiki')
            self.unicast(response)

    def _unsubscribe_from_wiki(self, uuid: UUID):
            wiki_id = self.user_to_wiki[uuid]
            self.wiki_to_users[wiki_id].remove(uuid)
            del(self.user_to_wiki[uuid])

    def unicast(self, message: UnicastMessage):
        uuid = message.identifier.uuid
        handler = self.user_to_handler[uuid]
        handler.write_json(message)

    def broadcast(self, object_id: ObjectId, message: BroadcastMessage):
        for uuid in self.broadcast_map[object_id]:
            handler = self.user_to_handler[uuid]
            handler.write_json(message)
