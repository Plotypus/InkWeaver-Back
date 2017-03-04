from loom.dispatchers.LAWProtocolDispatcher import LAWProtocolDispatcher
from loom.handlers.websockets.LoomHandler import LoomHandler
from loom.messages.incoming import (
    IncomingMessage, IncomingMessageFactory, SubscriptionIncomingMessage,
    SubscribeToStoryIncomingMessage, SubscribeToWikiIncomingMessage,
    UnsubscribeFromStoryIncomingMessage, UnsubscribeFromWikiIncomingMessage,
)
from loom.messages.outgoing import (
    UnicastMessage, StoryBroadcastMessage, WikiBroadcastMessage, OutgoingErrorMessage,
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
        self.story_to_uuids: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.wiki_to_uuids: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.uuid_to_user: Dict[UUID, ObjectId] = dict()
        self.uuid_to_story: Dict[UUID, ObjectId] = dict()
        self.uuid_to_wiki: Dict[UUID, ObjectId] = dict()
        self.uuid_to_handler: Dict[UUID, LoomHandler] = dict()

    async def process_incoming(self, handler: LoomHandler, message: JSON, action: str, uuid: UUID, message_id=None):
        # Receive the message and format it into one of our IncomingMessage objects.
        try:
            # Prepare potential additional arguments.
            user_id = self.uuid_to_user[uuid]
            story_id = self.uuid_to_story.get(uuid)
            wiki_id = self.uuid_to_wiki.get(uuid)
            additional_args = {'user_id': user_id}
            if story_id is not None:
                additional_args['story_id'] = story_id
            if wiki_id is not None:
                additional_args['wiki_id'] = wiki_id
            message_object: IncomingMessage = self.message_factory.build_message(self, action, message, additional_args)
        # Bad action.
        except ValueError:
            return self.dispatcher.format_failure_json(message_id, f"Action '{action}' not supported.")
        # Bad message format.
        except TypeError as e:
            # TODO: Replace with with a more specific error
            message = e.args[0]
            return self.dispatcher.format_failure_json(message_id, message)
        # Check whether the user is already connected to the router.
        if uuid not in self.uuid_to_handler:
            self.uuid_to_handler[uuid] = handler
        # Check if the new message is meant for subscription.
        if isinstance(message_object, SubscriptionIncomingMessage):
            if isinstance(message_object, SubscribeToStoryIncomingMessage):
                self.subscribe_to_story(message_object.story_id, uuid, message_id)
            elif isinstance(message_object, SubscribeToWikiIncomingMessage):
                self.subscribe_to_wiki(message_object.wiki_id, uuid, message_id)
            elif isinstance(message_object, UnsubscribeFromStoryIncomingMessage):
                self.unsubscribe_from_story(uuid, message_id)
            elif isinstance(message_object, UnsubscribeFromWikiIncomingMessage):
                self.unsubscribe_from_wiki(uuid, message_id)
            else:
                raise RuntimeError(f"unknown instance of SubscriptionIncomingMessage: {message_object}")
        else:
            # Dispatch the incoming message and process the response.
            response = await message_object.dispatch()
            if isinstance(response, UnicastMessage):
                self.unicast(response)
            elif isinstance(response, StoryBroadcastMessage):
                self.broadcast_to_story(story_id, response)
            elif isinstance(response, WikiBroadcastMessage):
                self.broadcast_to_wiki(wiki_id, response)
            else:
                raise RuntimeError(f"unknown instance of OutgoingMessage: {response}")

    def connect(self, handler: LoomHandler, user_id: ObjectId):
        uuid = handler.uuid
        self.uuid_to_handler[uuid] = handler
        self.uuid_to_user[uuid] = user_id

    def disconnect(self, handler: LoomHandler):
        uuid = handler.uuid
        self._unsubscribe_from_story(uuid)
        self._unsubscribe_from_wiki(uuid)
        del(self.uuid_to_handler[uuid])

    def subscribe_to_story(self, story_id: ObjectId, uuid: UUID, message_id: int):
        if uuid in self.uuid_to_story:
            # The user is already subscribed to another story.
            err_msg = OutgoingErrorMessage(uuid, message_id,
                                           error_message="Cannot subscribe to multiple stories.")
            self.unicast(err_msg)
        else:
            self.story_to_uuids[story_id].add(uuid)
            self.uuid_to_story[uuid] = story_id
            response = SubscribeToStoryOutgoingMessage(uuid, message_id)
            self.unicast(response)

    def subscribe_to_wiki(self, wiki_id: ObjectId, uuid: UUID, message_id: int):
        if uuid in self.uuid_to_wiki:
            # The user is already subscribed to another wiki.
            err_msg = OutgoingErrorMessage(uuid, message_id,
                                           error_message="Cannot subscribe to multiple wikis.")
            self.unicast(err_msg)
        else:
            self.wiki_to_uuids[wiki_id].add(uuid)
            self.uuid_to_wiki[uuid] = wiki_id
            response = SubscribeToWikiOutgoingMessage(uuid, message_id)
            self.unicast(response)

    def unsubscribe_from_story(self, uuid: UUID, message_id: int):
        if uuid not in self.uuid_to_story:
            # The user is not currently subscribed to any story.
            err_msg = OutgoingErrorMessage(uuid, message_id,
                                           error_message="Cannot unsubscribe from story; no active story subscription.")
            self.unicast(err_msg)
        else:
            self._unsubscribe_from_story(uuid)
            response = UnsubscribeFromStoryOutgoingMessage(uuid, message_id)
            self.unicast(response)

    def _unsubscribe_from_story(self, uuid: UUID):
            story_id = self.uuid_to_story[uuid]
            self.story_to_uuids[story_id].remove(uuid)
            del(self.uuid_to_story[uuid])

    def unsubscribe_from_wiki(self, uuid: UUID, message_id: int):
        if uuid not in self.uuid_to_wiki:
            # The user is not currently subscribed to any wiki.
            err_msg = OutgoingErrorMessage(uuid, message_id,
                                           error_message="Cannot unsubscribe from wiki; no active wiki subscription.")
            self.unicast(err_msg)
        else:
            self._unsubscribe_from_wiki(uuid)
            response = UnsubscribeFromWikiOutgoingMessage(uuid, message_id)
            self.unicast(response)

    def _unsubscribe_from_wiki(self, uuid: UUID):
            wiki_id = self.uuid_to_wiki[uuid]
            self.wiki_to_uuids[wiki_id].remove(uuid)
            del(self.uuid_to_wiki[uuid])

    def unicast(self, message: UnicastMessage):
        uuid = message.identifier.uuid
        handler = self.uuid_to_handler[uuid]
        handler.write_json(message)

    def broadcast_to_story(self, story_id: ObjectId, message: StoryBroadcastMessage):
        for uuid in self.story_to_uuids[story_id]:
            handler = self.uuid_to_handler[uuid]
            handler.write_json(message)

    def broadcast_to_wiki(self, wiki_id: ObjectId, message: WikiBroadcastMessage):
        for uuid in self.wiki_to_uuids[wiki_id]:
            handler = self.uuid_to_handler[uuid]
            handler.write_json(message)
