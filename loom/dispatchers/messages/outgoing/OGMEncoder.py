from .outgoing_message import OutgoingMessage

import json

from bson import ObjectId


class OGMEncoder(json.JSONEncoder):
    def default(self, o):
        print(f"In OGMEncoder with object: {o}")
        if isinstance(o, OutgoingMessage):
            # Recur on the body object
            return self.default(vars(o))
        if isinstance(o, ObjectId):
            # Tentative ObjectId format
            return f'{{"$oid": "{str(o)}"}}'
        if isinstance(o, list):
            # Recur on each of the elements in the list
            insides = [self.default(value) for value in o]
            return f'[{", ".join(insides)}]'
        if isinstance(o, dict):
            # Build dict object
            insides = [f'"{key}": {self.default(value)}' for key, value in o.items()]
            return f'{{{", ".join(insides)}}}'
        if isinstance(o, str):
            # Return the string object with quotes around it
            return f'"{o}"'
        if isinstance(o, int):
            return str(o)
        if isinstance(o, bool):
            return str(o)
        else:
            return json.JSONEncoder.default(self, o)
