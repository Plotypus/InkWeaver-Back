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


async def get_default_user():
    default_user = await _USERS.find_one({'_id': 'default_user'})
    if default_user:
        return default_user
    user = {
        '_id': 'default_user',
        'username':    'default',
        'password':    'default',
        'name':        'Default User',
        'email':       'defaultuser@default.com',
        'pen_name':    'Default Pen Name',
        'avatar':      None,
        'stories':     list(),
        'wikis':       list(),
        'preferences': None,
        'statistics':  None,
        'bio':         None,
    }
    await _USERS.insert_one(user)
    return user


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


async def create_story(user_id: ObjectId, wiki_id: ObjectId, title: str, publication_name: str, synopsis=None) -> ObjectId:
    story = {
        'owner':         {
            "user_id":          user_id,
            "publication_name": publication_name,
        },
        'wiki_id':       wiki_id,
        'collaborators': list(),
        'title':         title,
        'synopsis':      synopsis,
        'head_chapter':  None,
        'tail_chapter':  None,
        'statistics':    None,
        'settings':      None,
    }
    result = await _STORIES.insert_one(story)           # type: pymongo.results.InsertOneResult
    story_id = result.inserted_id
    await _add_story_to_user(user_id, story_id)
    return story_id


async def get_story(story_id: ObjectId):
    result = await _STORIES.find_one({'_id': story_id})
    return result


async def get_all_chapter_summaries(story_id: ObjectId):
    chapters = []
    story = await get_story(story_id)
    cur_id = story['head_chapter']
    while cur_id:
        chapter = await get_chapter(cur_id)
        chapters.append({
            'title':    chapter['title'],
            'id':       cur_id
        })  # TODO: Revise chapter summary structure
        cur_id = chapter['succeeded_by']
    return chapters


async def get_remaining_chapters(chapter_id: ObjectId):
    return await get_n_succeeding_chapters(chapter_id)


async def get_n_succeeding_chapters(chpater_id: ObjectId, num_chapters=None):
    ...


async def _add_story_to_user(user_id, story_id):
    await _USERS.update_one({'_id': user_id}, {'$push': {'stories': story_id}})


async def add_collaborator_to_story(user_id: ObjectId, publication_name: str, story_id: ObjectId):
    # TODO: Add user to story and story to user
    pass


async def update_head_chapter_of_story(story_id: ObjectId, chapter_id: ObjectId):
    await _STORIES.update_one({'_id': story_id}, {'$set': {'head_chapter': chapter_id}})


async def update_tail_chapter_of_story(story_id: ObjectId, chapter_id: ObjectId):
    await _STORIES.update_one({'_id': story_id}, {'$set': {'tail_chapter': chapter_id}})


async def create_chapter(story_id: ObjectId, title, preceding_id=None, succeeding_id=None) -> ObjectId:
    chapter = {
        'story_id':       story_id,
        'title':          title,
        'head_paragraph': None,
        'tail_paragraph': None,
        'preceded_by':    preceding_id,
        'succeeded_by':   succeeding_id,
        'statistics':     None,
    }
    result = await _CHAPTERS.insert_one(chapter)        # type: pymongo.results.InsertOneResult
    chapter_id = result.inserted_id
    return chapter_id


async def get_chapter(chapter_id):
    result = await _CHAPTERS.find_one({'_id': chapter_id})
    return result


async def update_head_paragraph_of_chapter(chapter_id: ObjectId, paragraph_id: ObjectId):
    await _CHAPTERS.update_one({'_id': chapter_id}, {'$set': {'head_paragraph': paragraph_id}})


async def update_tail_paragraph_of_chapter(chapter_id: ObjectId, paragraph_id: ObjectId):
    await _CHAPTERS.update_one({'_id': chapter_id}, {'$set': {'tail_paragraph': paragraph_id}})


async def update_chapters_succeeded_by(preceding_id: ObjectId, new_chapter_id: ObjectId):
    await _CHAPTERS.update_one({'_id': preceding_id}, {'$set': {'succeeded_by': new_chapter_id}})


async def update_chapters_preceded_by(succeeding_id: ObjectId, new_chapter_id: ObjectId):
    await _CHAPTERS.update_one({'_id': succeeding_id}, {'$set': {'preceded_by': new_chapter_id}})


async def create_paragraph(chapter_id: ObjectId, preceding_id=None, succeeding_id=None, text=None):
    paragraph = {
        'chapter_id': chapter_id,
        'text':       text,
        'statistics': None,
        'preceded_by':  preceding_id,
        'succeeded_by': succeeding_id,
    }
    result = await _PARAGRAPHS.insert_one(paragraph)    # type: pymongo.results.InsertOneResult
    paragraph_id = result.inserted_id
    return paragraph_id


async def get_paragraph(paragraph_id: ObjectId):
    result = await _PARAGRAPHS.find_one({'_id': paragraph_id})
    return result


async def update_paragraphs_succeeded_by(preceding_id: ObjectId, new_paragraph_id: ObjectId):
    await _PARAGRAPHS.update_one({'_id': preceding_id}, {'$set': {'succeeded_by': new_paragraph_id}})


async def update_paragraphs_preceded_by(succeeding_id: ObjectId, new_paragraph_id: ObjectId):
    await _PARAGRAPHS.update_one({'_id': succeeding_id}, {'$set': {'preceded_by': new_paragraph_id}})

