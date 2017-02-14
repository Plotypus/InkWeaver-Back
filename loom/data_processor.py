from loom.database.interfaces import AbstractDBInterface
from loom.dispatchers.demo import DemoDataDispatcher
from loom.serialize import decode_string_to_bson, encode_bson_to_string

import re

from bson import ObjectId
from typing import Dict

JSON = Dict


class DataProcessor:
    def __init__(self, interface):
        self._interface = interface
        self._dispatcher = DemoDataDispatcher(self.interface)
        self.responses = {}

    @property
    def interface(self) -> AbstractDBInterface:
        return self._interface

    @property
    def dispatcher(self):
        return self._dispatcher

    async def load_file(self, filename):
        with open(filename) as json_file:
            json_string = json_file.read()
        json = decode_string_to_bson(json_string)
        user_id = await self.create_user(json['user'])
        await self.process_list(json['dispatch_list'])
        return user_id

    async def create_user(self, user_json):
        user_id = await self.interface.create_user(**user_json)
        self.dispatcher.set_user_id(user_id)
        return user_id

    id_regex = re.compile(r'\$\{([^}]+)\}')

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
            m_id = int(m_id)
            keys = keys.split('.')
            response = self.responses[m_id]
            for key in keys:
                response = response[key]
            return response
        matches = re.finditer(self.id_regex, value)
        for match in matches:
            string_parts.append(value[prev_end:match.start()])
            m_id, keys = match.group(1).split('.', 1)
            m_id = int(m_id)
            keys = keys.split('.')
            response = self.responses[m_id]
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

    async def process_list(self, dispatch_list):
        for dispatch_item in dispatch_list:
            revised: JSON = {k: self.replace_id(v) for k, v in dispatch_item.items()}
            action = revised.pop('action')
            message_id = revised.get('message_id')
            response = await self.dispatcher.dispatch(revised, action, message_id)
            if message_id is not None:
                self.responses[message_id] = response
