from loom.database.interfaces import AbstractDBInterface
from loom.dispatchers import DemoDataDispatcher
from loom.serialize import encode_string_to_bson

import asyncio
import re

from typing import Dict

JSON = Dict


# from loom.database.interfaces import MongoDBAsyncioInterface
# i = MongoDBAsyncioInterface('test-db', 'localhost', 27017)
# from loom.data_processor import DataProcessor
# dp = DataProcessor(i)
# dp.load_file('/Users/pdarragh/Development/Plotypus/loom/scripts/christmas_carol.json')


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

    def load_file(self, filename):
        with open(filename) as json_file:
            json_string = json_file.read()
        json = encode_string_to_bson(json_string)
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.create_user(json['user']))
        event_loop.run_until_complete(self.process_list(json['dispatch_list']))
        event_loop.close()

    async def create_user(self, user_json):
        user_id = await self.interface.create_user(**user_json)
        self.dispatcher.set_user_id(user_id)

    id_regex = re.compile(r'\$\{([^}]+)\}')

    def replace_id(self, value):
        if not isinstance(value, str):
            return value
        match = re.fullmatch(self.id_regex, value)
        if match is None:
            return value
        else:
            m_id, keys = match.group(1).split('.', 1)
            m_id = int(m_id)
            keys = keys.split('.')
            response = self.responses[m_id]
            for key in keys:
                response = response[key]
            return response

    async def process_list(self, dispatch_list):
        for dispatch_item in dispatch_list:
            revised: JSON = {k: self.replace_id(v) for k, v in dispatch_item.items()}
            action = revised.pop('action')
            message_id = revised.get('message_id')
            print("action: {}".format(action))
            for key, value in revised.items():
                print("    {}: {}".format(key, value))
            response = await self.dispatcher.dispatch(revised, action, message_id)
            if message_id is not None:
                self.responses[message_id] = response
