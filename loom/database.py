import motor.motor_tornado
import pymongo.results

from bson.objectid import ObjectId

# Connection parameters.
_HOST = 'localhost'
_PORT = 27017

# Connect to the database.
_DB_CLIENT = motor.motor_tornado.MotorClient(_HOST, _PORT)
_DB = _DB_CLIENT.inkweaver

# Define our collections.
_USERS               = _DB.users                        # type: motor.core.AgnosticCollection
_STORIES             = _DB.stories                      # type: motor.core.AgnosticCollection
_CHAPTERS            = _DB.chapters                     # type: motor.core.AgnosticCollection
_PARAGRAPHS          = _DB.paragraphs                   # type: motor.core.AgnosticCollection
_WIKIS               = _DB.wikis                        # type: motor.core.AgnosticCollection
_CATEGORIES          = _DB.categories                   # type: motor.core.AgnosticCollection
_PAGES               = _DB.pages                        # type: motor.core.AgnosticCollection
_SECTIONS            = _DB.sections                     # type: motor.core.AgnosticCollection
_LINKS               = _DB.links                        # type: motor.core.AgnosticCollection
_STORY_REFERENCES    = _DB.story_references             # type: motor.core.AgnosticCollection
_WIKI_REFERENCES     = _DB.wiki_references              # type: motor.core.AgnosticCollection


def set_db_host(host):
    global _HOST
    _HOST = host


def set_db_port(port):
    global _PORT
    _PORT = port


def hex_string_to_bson_oid(s):
    return ObjectId(s)


async def create_user(username, password, name, email, pen_name=None):
    user = {
        'username':    username,
        'password':    password,
        'name':        name,
        'email':       email,
        'pen_name':    pen_name,
        'avatar':      None,
        'stories':     list(),
        'wikis':       list(),
        'preferences': None,
        'statistics':  None,
        'bio':         None,
    }
    result = await _USERS.insert_one(user)              # type: pymongo.results.InsertOneResult
    return result.inserted_id


async def get_user(user_id):
    result = await _USERS.find_one({'_id': user_id})
    return result


async def get_all_user_ids():
    result = []
    async for doc in _USERS.find():
        result.append(doc['_id'])
    return result


async def create_story(user_id, wiki_id, title, author_name=None, synopsis=None):
    story = {
        'user_id':     user_id,
        'wiki_id':     wiki_id,
        'title':       title,
        'author_name': author_name,
        'synopsis':    synopsis,
        'statistics':  None,
        'chapters':    list(),
        'settings':    None,
    }
    result = await _STORIES.insert_one(story)           # type: pymongo.results.InsertOneResult
    story_id = result.inserted_id
    await _add_story_to_user(user_id, story_id)
    return story_id


async def get_story(story_id):
    result = await _STORIES.find_one({'_id': story_id})
    return result


async def _add_story_to_user(user_id, story_id):
    await _USERS.update_one({'_id': user_id}, {'$push': {'stories': story_id}})


async def create_chapter(story_id, title=None):
    chapter = {
        'story_id':     story_id,
        'title':        title,
        'paragraphs':   list(),
        'statistics':   None,
    }
    result = await _CHAPTERS.insert_one(chapter)        # type: pymongo.results.InsertOneResult
    chapter_id = result.inserted_id
    await _add_chapter_to_story(story_id, chapter_id)
    return chapter_id


async def get_chapter(chapter_id):
    result = await _CHAPTERS.find_one({'_id': chapter_id})
    return result


async def _add_chapter_to_story(story_id, chapter_id):
    await _STORIES.update_one({'_id': story_id}, {'$push': {'chapters': chapter_id}})


async def create_paragraph(chapter_id, text=None):
    paragraph = {
        'chapter_id': chapter_id,
        'text': text,
        'statistics': None,
    }
    result = await _PARAGRAPHS.insert_one(paragraph)    # type: pymongo.results.InsertOneResult
    paragraph_id = result.inserted_id
    await _add_paragraph_to_chapter(chapter_id, paragraph_id)


async def _add_paragraph_to_chapter(chapter_id, paragraph_id):
    pass
