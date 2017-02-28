from .outgoing_message import OutgoingMessage

import json

from bson import ObjectId


class OGMEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, OutgoingMessage):
            # Recur on the body object
            return self.default(vars(o))
        if isinstance(o, ObjectId):
            # Tentative ObjectId format
            return {'$oid': str(o)}
        if isinstance(o, list):
            # Recur on each of the elements in the list
            insides = [self.default(value) for value in o]
            return insides
        if isinstance(o, dict):
            # Build dict object
            insides = {key: self.default(value) for key, value in o.items()}
            return insides
        else:
            return o
