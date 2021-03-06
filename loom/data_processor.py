from loom.dispatchers.DemoDataDispatcher import DemoDataDispatcher
from loom.messages import IncomingMessage, OutgoingMessage
from loom.messages.incoming.demo import DemoIncomingMessageFactory
from loom.messages.outgoing import GetWikiInformationOutgoingMessage, GetStoryInformationOutgoingMessage
from loom.serialize import decode_string_to_bson, encode_bson_to_string

import re

from bson import ObjectId
from typing import Dict

JSON = Dict


class DataProcessor:
    def __init__(self, interface):
        self.dispatcher = DemoDataDispatcher(interface)
        self.message_factory = DemoIncomingMessageFactory()
        self.responses = {}

    async def load_file(self, filename, approve_passive_links: bool):
        with open(filename) as json_file:
            json_string = json_file.read()
        json = decode_string_to_bson(json_string)
        user_json = json['user']
        wiki_json = json['wiki']
        story_json = json['story']
        extra_users_json = json['extra_users']
        user_id = await self.create_user(user_json)
        wiki_id = await self.create_wiki(user_id, wiki_json)
        # Delete the default wiki setup, we don't want it for data loading.
        wiki = await self.dispatcher.db_interface.get_wiki(wiki_id)
        child_segment = await self.dispatcher.db_interface.get_segment(wiki['segment_id'])
        for segment in child_segment['segments']:
            await self.dispatcher.db_interface.delete_segment(wiki_id, segment['segment_id'])
        story_id = await self.create_story(user_id, wiki_id, story_json)
        for extra_user_json in extra_users_json:
            await self.create_user(extra_user_json)
        await self.process_list(json['dispatch_list'], user_id, wiki_id, story_id)
        if approve_passive_links:
            wiki_alias_list = await self.dispatcher.db_interface.get_wiki_alias_list(wiki_id)
            for alias in wiki_alias_list:
                for passive_link in alias['passive_links']:
                    await self.dispatcher.db_interface.approve_passive_link(passive_link['passive_link_id'], story_id,
                                                                            wiki_id)

    async def create_user(self, user_json):
        user_id = await self.dispatcher.db_interface.create_user(**user_json)
        return user_id

    async def create_wiki(self, user_id, wiki_json):
        wiki_id = await self.dispatcher.db_interface.create_wiki(user_id, **wiki_json)
        return wiki_id

    async def create_story(self, user_id, wiki_id, story_json):
        story_id = await self.dispatcher.db_interface.create_story(user_id, wiki_id=wiki_id, **story_json)
        return story_id

    async def process_list(self, dispatch_list, user_id, wiki_id, story_id):
        additional_args = {
            'user_id': user_id,
            'wiki_id': wiki_id,
            'story_id': story_id,
        }
        # self.responses['user'] = await self.dispatcher.db_interface.get_user_preferences(user_id)
        wiki_dict = await self.dispatcher.db_interface.get_wiki(wiki_id)
        wiki_message = GetWikiInformationOutgoingMessage('', '',
                                                 wiki_title=wiki_dict['title'],
                                                 segment_id=wiki_dict['segment_id'],
                                                 users=wiki_dict['users'],
                                                 summary=wiki_dict['summary'])
        wiki_message.wiki_id = wiki_id
        self.responses['wiki'] = wiki_message
        story_dict = await self.dispatcher.db_interface.get_story(story_id)
        story_message = GetStoryInformationOutgoingMessage('', '',
                                                   story_title=story_dict['title'],
                                                   section_id=story_dict['section_id'],
                                                   wiki_id=story_dict['wiki_id'],
                                                   users=story_dict['users'])
        story_message.story_id = story_id
        self.responses['story'] = story_message
        for dispatch_item in dispatch_list:
            revised: JSON = {k: self.replace_id(v) for k, v in dispatch_item.items()}
            action = revised.pop('action')
            message: IncomingMessage = self.message_factory.build_message(self.dispatcher, action, revised, additional_args)
            async for response in message.dispatch():
                if message.message_id is not None:
                    self.responses[str(message.message_id)] = response

    id_regex = re.compile(r'\$\{([^}]+)\}')

    # TODO: Fix this! Need to handle new wiki IDs/story IDs.
    def replace_id(self, value):
        if isinstance(value, dict):
            revised = {k: self.replace_id(v) for k, v in value.items()}
            return revised
        if not isinstance(value, str):
            return value
        string_parts = []
        prev_end = 0
        fullmatch = re.fullmatch(self.id_regex, value)
        if fullmatch is not None:
            m_id, keys = fullmatch.group(1).split('.', 1)
            keys = keys.split('.')
            response = vars(self.responses[m_id])
            for key in keys:
                response = response[key]
            return response
        matches = re.finditer(self.id_regex, value)
        for match in matches:
            string_parts.append(value[prev_end:match.start()])
            m_id, keys = match.group(1).split('.', 1)
            keys = keys.split('.')
            response = vars(self.responses[m_id])
            for key in keys:
                response = response[key]
            if isinstance(response, ObjectId):
                # TODO: Update this fix
                # Remove the whitespace in the ObjectId's encoding.
                response = encode_bson_to_string(response).replace(' ', '')
            prev_end = match.end()
            string_parts.append(response)
        string_parts.append(value[prev_end:])
        return ''.join(string_parts)
