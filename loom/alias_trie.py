from bson.objectid import ObjectId
from typing import List, Union


class AliasTrieMatch:
    def __init__(self, length, page_id, alias_id):
        self.length = length
        self.page_id = page_id
        self.alias_id = alias_id


class AliasTrie:
    def __init__(self):
        self.root = AliasTrieNode(None, is_terminal=True, page_id=None, alias_id=None, depth=0)

    def add_path(self, path: List[str], page_id: ObjectId, alias_id: ObjectId):
        if not path:
            return
        node = self.root
        for i in range(len(path)):
            token = path[i]
            next_node = node.get_child(token)
            if next_node is None:
                next_node = AliasTrieNode(token, is_terminal=False, page_id=None, alias_id=None, depth=i+1)
                node.add_child(next_node)
            node = next_node
        node.is_terminal = True
        node.page_id = page_id
        node.alias_id = alias_id

    def find_longest_match_in_tokens(self, tokens, *, from_index) -> Union[AliasTrieMatch, None]:
        node = self.root.find_next_terminal(tokens, from_index, None)
        if node.depth > 0:
            return AliasTrieMatch(from_index + node.depth, node.page_id, node.alias_id)
        else:
            return None


class AliasTrieNode:
    def __init__(self, value: Union[str, None], *, is_terminal: bool, page_id: Union[ObjectId, None],
                 alias_id: Union[ObjectId, None], depth: int):
        self.is_terminal = is_terminal
        self.children = {}
        self.page_id = page_id
        self.alias_id = alias_id
        self.depth = depth
        self.value = value

    def find_next_terminal(self, tokens, next_token_index: int, last_terminal_node):  # -> AliasTrieNode
        last_terminal_node = self if self.is_terminal else last_terminal_node
        if not tokens or next_token_index >= len(tokens):
            return last_terminal_node
        token = tokens[next_token_index]
        next_node = self.get_child(token)
        if next_node is None:
            return last_terminal_node
        else:
            return next_node.find_next_terminal(tokens, next_token_index + 1, last_terminal_node)

    def get_child(self, child: str):
        return self.children.get(child)

    def add_child(self, child):
        self.children[child.value] = child
