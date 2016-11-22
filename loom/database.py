import motor.motor_tornado
import pymongo.results

from bson.objectid import ObjectId

# Connection parameters.
_HOST = 'localhost'
_PORT = 27017


def set_db_host(host):
    global _HOST
    _HOST = host


def set_db_port(port):
    global _PORT
    _PORT = port


# Connect to the database.
_DB_CLIENT = motor.motor_tornado.MotorClient(_HOST, _PORT)
_DB = _DB_CLIENT.inkweaver

# Define our collections.
USERS               = _DB.users                 # type: motor.core.AgnosticCollection
STORIES             = _DB.stories               # type: motor.core.AgnosticCollection
CHAPTERS            = _DB.chapters              # type: motor.core.AgnosticCollection
PARAGRAPHS          = _DB.paragraphs            # type: motor.core.AgnosticCollection
WIKIS               = _DB.wikis                 # type: motor.core.AgnosticCollection
CATEGORIES          = _DB.categories            # type: motor.core.AgnosticCollection
PAGES               = _DB.pages                 # type: motor.core.AgnosticCollection
SECTIONS            = _DB.sections              # type: motor.core.AgnosticCollection
LINKS               = _DB.links                 # type: motor.core.AgnosticCollection
STORY_REFERENCES    = _DB.story_references      # type: motor.core.AgnosticCollection
WIKI_REFERENCES     = _DB.wiki_references       # type: motor.core.AgnosticCollection


async def get_all_user_ids():
    result = []
    async for doc in USERS.find():
        result.append(str(doc['_id']))
    return result


async def get_user(user_id):
    result = await USERS.find_one({'_id': ObjectId(user_id)})
    return result


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
    result = await USERS.insert_one(user)       # type: pymongo.results.InsertOneResult
    return str(result.inserted_id)


async def add_story_to_user(user_id, story_id):
    await USERS.update_one({'_id': ObjectId(user_id)}, {'$push': {'stories': story_id}})


async def get_story(story_id):
    result = await STORIES.find_one({'_id': ObjectId(story_id)})
    return result


async def create_story(user_id, wiki_id, title, author_name=None, synopsis=None):
    # TODO: Attach story to user
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
    result = await STORIES.insert_one(story)    # type: pymongo.results.InsertOneResult
    story_id = str(result.inserted_id)
    await add_story_to_user(user_id, story_id)
    return story_id
