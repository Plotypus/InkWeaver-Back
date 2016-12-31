import motor.motor_tornado
import pymongo.results

from bson.objectid import ObjectId
from typing import Dict, List

# Connection parameters.
_HOST = 'localhost'
_PORT = 27017

# Connect to the database.
_DB_CLIENT = motor.motor_tornado.MotorClient(_HOST, _PORT)
_DB = _DB_CLIENT.inkweaver

# Define our collections.
## User
_USERS              = _DB.users                         # type: motor.core.AgnosticCollection

## Stories
_STORIES            = _DB.stories                       # type: motor.core.AgnosticCollection
_SECTIONS           = _DB.sections                      # type: motor.core.AgnosticCollection

## Wikis
_WIKIS              = _DB.wikis                         # type: motor.core.AgnosticCollection
_SEGMENTS           = _DB.segments                      # type: motor.core.AgnosticCollection
_PAGES              = _DB.pages                         # type: motor.core.AgnosticCollection
_HEADINGS           = _DB.headings                      # type: motor.core.AgnosticCollection

## Content
_CONTENT            = _DB.content                       # type: motor.core.AgnosticCollection
_PARAGRAPHS         = _DB.paragraphs                    # type: motor.core.AgnosticCollection


def set_db_host(host):
    global _HOST
    _HOST = host


def set_db_port(port):
    global _PORT
    _PORT = port


def get_db_host():
    return _HOST


def get_db_port():
    return _PORT


def hex_string_to_bson_oid(s):
    return ObjectId(s)


############################################################
##
## User Related Methods
##
############################################################


async def create_user(username: str, password, name: str, email: str, bio: str, avatar=None, _id=None) -> ObjectId:
    """Inserts a new user to the users collection.

    Adds a new user to the users collection. Stories and wikis are initialized
    to empty lists. Unless `_id` is provided, a random BSON ObjectId will be
    assigned to `_id`. Currently, statistics are not implemented.

    Args:
        username: The username of the user.
        password: The salted hash of the user's password.
        name: The full name of the user.
        email: The email address of the user.
        bio: A short description of the user.
        avatar (str): Base-64 encoded image user chooses to identify
            themselves with.
        _id (ObjectId): `_id` is optional, but if provided, will create a user
            with the provided ObjectId.

    Returns:
        The ObjectId that is associated with the newly created user. If `_id`
        was provided, `_id` will be returned. Otherwise, a randomly generated
        BSON ObjectId will be returned.

    """
    user = {
        'username':   username,
        'password':   password,
        'name':       name,
        'email':      email,
        'bio':        bio,
        'avatar':     avatar,
        'stories':    list(),
        'wikis':      list(),
        'statistics': None,
    }
    if _id is not None:
        user['_id'] = _id
    result = await _USERS.insert_one(user)
    return result.inserted_id


async def get_user_preferences(user_id: ObjectId) -> Dict:
    """Grabs the preferences for the provided user.

    Finds the user in the database and extracts the fields specified by
    The LAW Protocol.

    Args:
        user_id: BSON ObjectId of user to query for.

    Returns:
        A filtered document of the user. By The Law Protocol, returns
        `username`, `name`, `email`, `bio`, and `avatar` of the user.

    """
    result = await _USERS.find_one(
        filter={'_id': user_id},
        projection={
            '_id':      0,
            'username': 1,
            'name':     1,
            'email':    1,
            'bio':      1,
            'avatar':   1,
        }
    )
    return result


async def get_user_story_ids(user_id: ObjectId) -> List[ObjectId]:
    """Grabs the ObjectIds of the user's stories.

    Args:
        user_id: BSON ObjectId of user to query for.

    Returns:
        A list of the BSON ObjectIds of the `stories` that the user has access
        to.

    """
    result = await _USERS.find_one(
        filter={'_id': user_id},
        projection={
            '_id':     0,
            'stories': 1,
        }
    )
    return result['stories']


async def get_user_wiki_ids(user_id: ObjectId) -> List[ObjectId]:
    """Grabs the ObjectIds of the user's wikis.

    Args:
        user_id: BSON ObjectId of user to query for.

    Returns:
        A list of the BSON ObjectIds of the `wikis` that the user has access to.

    """
    result = await _USERS.find_one(
        filter={'_id': user_id},
        projection={
            '_id':   0,
            'wikis': 1,
        }
    )
    return result['wikis']


async def get_user_story_and_wiki_ids(user_id: ObjectId) -> Dict:
    """Grabs the ObjectIds of the user's stories.

    Args:
        user_id: BSON ObjectId of user to query for.

    Returns:
        A dict containing the BSON ObjectIds for the `stories` and `wikis`
        that the user has access to.

    """
    result = await _USERS.find_one(
        filter={'_id': user_id},
        projection={
            '_id':     0,
            'stories': 1,
            'wikis':   1,
        }
    )
    return result


############################################################
##
## Story Related Methods
##
############################################################


async def create_story(title: str, wiki_id: ObjectId, user_description, summary: str, section_id: ObjectId, _id=None) -> ObjectId:
    """Inserts a new story to the stories collection.

    Adds a new story to the stories collection. A section for the story should
    be created before calling this function, in which the `section_id` is
    specified. `_id` is optional and if provided will create the story with the
    given `_id`, rather than the generated BSON ObjectId. Currently, statistics
    and settings are unimplemented.

    Args:
        title: The title of the story.
        wiki_id: The unique ID of the associated wiki.
        user_description: A dict containing information of the story's owner.
            A user description contains a `user_id`, `name`, and `access_level`.

            `user_description` args:
                user_id (ObjectId): The unique ID of the user.
                name (str): The name of the user.
                access_level (str): A description of the user's privileges in
                    the story.
        summary: A brief summary of the story.
        section_id: The unique ID of the story's recursive section
            representation.
        _id (ObjectId): `_id` is optional, but if provided will create a story
            with the provided ObjectId.

    Returns:
        The ObjectId that is associated with the newly created story. If `_id`
        was provided, `_id` will be returned. Otherwise, a randomly generated
        BSON ObjectId will be returned.
    """
    story = {
        'title':      title,
        'wiki_id':    wiki_id,
        'users':      [user_description],
        'summary':    summary,
        'section_id': section_id,
        'statistics': None,
        'settings':   None,
    }
    if _id is not None:
        story['_id'] = _id
    result = await _STORIES.insert_one(story)
    return result.inserted_id


async def create_section(title: str, content_id: ObjectId, _id=None) -> ObjectId:
    """

    Args:
        title:
        content_id:
        _id:

    Returns:

    """
    section = {
        'title':         title,
        'content_id':    content_id,
        'pre_sections':  list(),
        'sections':      list(),
        'post_sections': list(),
        'statistics':    None,
    }
    if _id is not None:
        section['_id'] = _id
    result = await _SECTIONS.insert_one(section)
    return result.inserted_id


async def get_story_information(story_id: ObjectId):
    """

    Args:
        story_id:

    Returns:

    """
    result = await _STORIES.find_one({'_id': story_id})
    return result


############################################################
##
## Wiki Related Methods
##
############################################################


async def create_wiki(title: str, user_description, summary: str, segment_id: ObjectId, _id=None) -> ObjectId:
    """

    Args:
        title:
        user_description:
        summary:
        segment_id:
        _id:

    Returns:

    """
    wiki = {
        'title':      title,
        'users':      [user_description],
        'summary':    summary,
        'segment_id': segment_id,
        'statistics': None,
        'settings':   None,
    }
    if _id is not None:
        wiki['_id'] = _id
    result = await _WIKIS.insert_one(wiki)
    return result.inserted_id


async def create_segment(title: str, _id=None) -> ObjectId:
    """

    Args:
        title:
        _id:

    Returns:

    """
    segment = {
        'title':             title,
        'segments':          list(),
        'pages':             list(),
        'template_headings': list(),
        'statistics':        None,
    }
    if _id is not None:
        segment['_id'] = _id
    result = await _SEGMENTS.insert_one(segment)
    return result.inserted_id


async def create_page(title: str, _id=None) -> ObjectId:
    """

    Args:
        title:
        _id:

    Returns:

    """
    page = {
        'title':      title,
        'headings':   list(),
        'references': None,
        'aliases':    None,
    }
    if _id is not None:
        page['_id'] = _id
    result = await _PAGES.insert_one(page)
    return result.inserted_id


async def create_heading(title: str, content_id: ObjectId, _id=None) -> ObjectId:
    """

    Args:
        title:
        content_id:
        _id:

    Returns:

    """
    heading = {
        'title': title,
        'content_id': content_id,
    }
    if _id is not None:
        heading['_id'] = _id
    result = await _HEADINGS.insert_one(heading)
    return result.inserted_id


############################################################
##
## Content Related Methods
##
############################################################


async def create_content(_id=None) -> ObjectId:
    """

    Args:
        _id:

    Returns:

    """
    content = {
        'paragraphs': list(),
    }
    if _id is not None:
        content['_id'] = _id
    result = await _CONTENT.insert_one(content)
    return result.inserted_id


async def create_paragraph(text: str, _id=None) -> ObjectId:
    """

    Args:
        text:
        _id:

    Returns:

    """
    paragraph = {
        'text':       text,
        'statistics': None,
    }
    if _id is not None:
        paragraph['_id'] = _id
    result = await _PARAGRAPHS.insert_one(paragraph)
    return result.inserted_id