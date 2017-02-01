from bson.json_util import dumps as __bson_encode, loads as __bson_decode
from tornado.escape import to_basestring


def encode_bson_to_string(dictionary):
    """
    Encode a BSON dictionary into a string.

    :param dictionary: the Python dictionary to be converted
    :return: a BSON string representation
    """
    # The following rationale was copied from tornado.escape.json_encode:
    #
    # JSON permits but does not require forward slashes to be escaped.
    # This is useful when json data is emitted in a <script> tag
    # in HTML, as it prevents </script> tags from prematurely terminating
    # the javascript.  Some json libraries do this escaping by default,
    # although python's standard library does not, so we do it here.
    # http://stackoverflow.com/questions/1580647/json-why-are-forward-slashes-escaped
    return __bson_encode(dictionary).replace("</", "<\\/")


def decode_string_to_bson(bson):
    """
    Decode a string into a BSON object dictionary.

    :param bson: the string to decode
    :return: a Python dictionary representation
    """
    basestring = to_basestring(bson)
    return __bson_decode(basestring)
