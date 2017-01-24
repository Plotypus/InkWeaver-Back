from loom.database.interfaces import AbstractDBInterface
from loom.dispatchers import DemoDataDispatcher
from loom.serialize import encode_string_to_bson

import re

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

    def load_file(self, filename):
        with open(filename) as json_file:
            json_string = json_file.read()
        json = encode_string_to_bson(json_string)
        self.create_user(json['user'])
        self.process_list(json['dispatch_list'])

    def create_user(self, user_json):
        user_id = self.interface.create_user(**user_json)
        self.dispatcher.set_user_id(user_id)

    id_regex = re.compile(r'\$\{([^}]+)\}')

    def replace_id(self, value):
        if not isinstance(value, str):
            return value
        match = re.fullmatch(self.id_regex, value)
        if match is None:
            return value
        else:
            id, keys = match.group(1).split('.', 1)
            keys = keys.split('.')
            response = self.responses[id]
            for key in keys:
                response = response[key]
            return response

    def process_list(self, dispatch_list):
        for dispatch_item in dispatch_list:
            revised: JSON = {k: self.replace_id(v) for k, v in dispatch_item.items()}
            action = revised.pop('action')
            message_id = revised.get('message_id')
            response = self.dispatcher.dispatch(revised, action, message_id)
            if message_id is not None:
                self.responses[message_id] = response
