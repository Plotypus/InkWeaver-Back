from loom.dispatchers.LAWProtocolDispatcher import LAWProtocolDispatcher
from loom.handlers.websockets.LoomHandler import LoomHandler
from loom.messages.incoming import (
    IncomingMessage, IncomingMessageFactory, SubscriptionIncomingMessage,
    SubscribeToStoryIncomingMessage, SubscribeToWikiIncomingMessage,
    UnsubscribeFromStoryIncomingMessage, UnsubscribeFromWikiIncomingMessage, UserSignOutIncomingMessage
)
from loom.messages.outgoing import (
    UnicastMessage, MulticastMessage, StoryBroadcastMessage, WikiBroadcastMessage, DualBroadcastMessage,
    OutgoingErrorMessage,
    SubscribeToStoryOutgoingMessage, SubscribeToWikiOutgoingMessage,
    UnsubscribeFromStoryOutgoingMessage, UnsubscribeFromWikiOutgoingMessage
)

from bson.objectid import ObjectId
from collections import defaultdict
from tornado.ioloop import IOLoop
from tornado.queues import Queue
from uuid import UUID

from typing import Dict, Set, Union
JSON = Dict


class Router:
    class MessageTuple:
        def __init__(self, handler: LoomHandler, message: JSON, action: str, uuid: UUID, message_id=None):
            self.handler = handler
            self.message = message
            self.action = action
            self.uuid = uuid
            self.message_id = message_id

    def __init__(self, interface):
        # Classes used throughout.
        self.dispatcher = LAWProtocolDispatcher(interface)
        self.message_factory = IncomingMessageFactory()
        self.message_tuples = Queue()
        # Various dictionaries for keeping track of user information.
        self.user_to_uuids: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.story_to_uuids: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.wiki_to_uuids: Dict[ObjectId, Set[UUID]] = defaultdict(set)
        self.uuid_to_user: Dict[UUID, ObjectId] = dict()
        self.uuid_to_story: Dict[UUID, ObjectId] = dict()
        self.uuid_to_wiki: Dict[UUID, ObjectId] = dict()
        self.uuid_to_handler: Dict[UUID, LoomHandler] = dict()
        # Begin reading from the queue.
        IOLoop.current().spawn_callback(self.process_tuples)

    async def enqueue_message(self, handler: LoomHandler, message: JSON, action: str, uuid: UUID, message_id=None):
        message_tuple = Router.MessageTuple(handler, message, action, uuid, message_id)
        await self.message_tuples.put(message_tuple)

    async def process_tuples(self):
        async for message_tuple in self.message_tuples:
            await self.handle_message_tuple(message_tuple)
            self.message_tuples.task_done()

    async def handle_message_tuple(self, message_tuple: MessageTuple):
        # Receive the message and format it into one of our IncomingMessage objects.
        try:
            # Prepare potential additional arguments.
            user_id = self.uuid_to_user[message_tuple.uuid]
            story_id = self.uuid_to_story.get(message_tuple.uuid)
            wiki_id = self.uuid_to_wiki.get(message_tuple.uuid)
            additional_args = {'user_id': user_id}
            if story_id is not None:
                additional_args['story_id'] = story_id
            if wiki_id is not None:
                additional_args['wiki_id'] = wiki_id
            message_object: IncomingMessage = self.message_factory.build_message(self.dispatcher, message_tuple.action,
                                                                                 message_tuple.message, additional_args)
        # Bad action.
        except ValueError:
            # Should write the message?
            error_message = self.dispatcher.format_failure_json(message_tuple.message_id,
                                                                f"Action '{message_tuple.action}' not supported.")
            self.unicast_error(message_tuple, error_message)
            return

        # Bad message format.
        except TypeError as e:
            # TODO: Replace with with a more specific error
            message = e.args[0]
            error_message = self.dispatcher.format_failure_json(message_tuple.message_id, message)
            self.unicast_error(message_tuple, error_message)
            return

        # Check whether the user is already connected to the router.
        if message_tuple.uuid not in self.uuid_to_handler:
            self.uuid_to_handler[message_tuple.uuid] = message_tuple.handler
        # Check if the new message is meant for subscription.
        if isinstance(message_object, SubscriptionIncomingMessage):
            if isinstance(message_object, SubscribeToStoryIncomingMessage):
                self.subscribe_to_story(message_object.story_id, message_tuple.uuid, message_tuple.message_id)
            elif isinstance(message_object, SubscribeToWikiIncomingMessage):
                self.subscribe_to_wiki(message_object.wiki_id, message_tuple.uuid, message_tuple.message_id)
            elif isinstance(message_object, UnsubscribeFromStoryIncomingMessage):
                self.unsubscribe_from_story(message_tuple.uuid, message_tuple.message_id)
            elif isinstance(message_object, UnsubscribeFromWikiIncomingMessage):
                self.unsubscribe_from_wiki(message_tuple.uuid, message_tuple.message_id)
            else:
                raise RuntimeError(f"unknown instance of SubscriptionIncomingMessage: {message_object}")
        elif isinstance(message_object, UserSignOutIncomingMessage):
            self.disconnect(message_tuple.handler)
        else:
            # Dispatch the incoming message and process the responses.
            async for response in message_object.dispatch():
                if isinstance(response, UnicastMessage):
                    self.unicast(response)
                elif isinstance(response, MulticastMessage):
                    self.multicast(response)
                elif isinstance(response, StoryBroadcastMessage):
                    self.broadcast_to_story(story_id, response)
                elif isinstance(response, WikiBroadcastMessage):
                    self.broadcast_to_wiki(wiki_id, response)
                elif isinstance(response, DualBroadcastMessage):
                    self.broadcast_to_story(story_id, response)
                    self.broadcast_to_wiki(wiki_id, response)
                else:
                    raise RuntimeError(f"unknown instance of OutgoingMessage: {response}")

    def connect(self, handler: LoomHandler, user_id: ObjectId):
        uuid = handler.uuid
        self.uuid_to_handler[uuid] = handler
        self.uuid_to_user[uuid] = user_id
        self.user_to_uuids[user_id].add(uuid)

    def disconnect(self, handler: LoomHandler):
        uuid = handler.uuid
        try:
            self._remove_uuid(uuid)
        except KeyError:
            pass
        try:
            self._unsubscribe_from_story(uuid)
        except KeyError:
            pass
        try:
            self._unsubscribe_from_wiki(uuid)
        except KeyError:
            pass
        try:
            del(self.uuid_to_handler[uuid])
        except KeyError:
            pass

    def _remove_uuid(self, uuid: UUID):
        user_id = self.uuid_to_user[uuid]
        del(self.uuid_to_user[uuid])
        self.user_to_uuids[user_id].remove(uuid)

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

    def multicast(self, message: MulticastMessage):
        uuid = message.identifier.uuid
        user_id = self.uuid_to_user[uuid]
        for handler_uuid in self.user_to_uuids[user_id]:
            handler = self.uuid_to_handler[handler_uuid]
            handler.write_json(message)

    def broadcast_to_story(self, story_id: ObjectId, message: Union[DualBroadcastMessage, StoryBroadcastMessage]):
        for uuid in self.story_to_uuids[story_id]:
            handler = self.uuid_to_handler[uuid]
            handler.write_json(message)

    def broadcast_to_wiki(self, wiki_id: ObjectId, message: Union[DualBroadcastMessage, WikiBroadcastMessage]):
        for uuid in self.wiki_to_uuids[wiki_id]:
            handler = self.uuid_to_handler[uuid]
            handler.write_json(message)

    def unicast_error(self, message_tuple: MessageTuple, error_msg: str):
        uuid = message_tuple.uuid
        handler = self.uuid_to_handler[uuid]
        handler.write_json(error_msg)
