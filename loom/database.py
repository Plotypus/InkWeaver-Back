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
_USERS              = _DB.users                         # type: motor.core.AgnosticCollection

_STORIES            = _DB.stories                       # type: motor.core.AgnosticCollection
_CHAPTERS           = _DB.chapters                      # type: motor.core.AgnosticCollection
_PARAGRAPHS         = _DB.paragraphs                    # type: motor.core.AgnosticCollection

_WIKI_SEGMENTS      = _DB.wiki_segments                 # type: motor.core.AgnosticCollection
_WIKI_PAGES         = _DB.wiki_pages                    # type: motor.core.AgnosticCollection
_WIKI_SECTIONS      = _DB.wiki_sections                 # type: motor.core.AgnosticCollection
_WIKI_PARAGRAPHS    = _DB.wiki_paragraphs               # type: motor.core.AgnosticCollection

_LINKS              = _DB.links                         # type: motor.core.AgnosticCollection
_STORY_REFERENCES   = _DB.story_references              # type: motor.core.AgnosticCollection
_WIKI_REFERENCES    = _DB.wiki_references               # type: motor.core.AgnosticCollection


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


############################################################
##
## Story Related Methods
##
############################################################


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


async def get_story_summary(story_id: ObjectId):
    story = await get_story(story_id)
    return get_summary_from_story(story)


def get_summary_from_story(story):
    # TODO: Revise story summary structure
    summary = {
        'title':    story['title'],
        'id':       story['_id'],
    }
    return summary


async def get_all_chapter_summaries(story_id: ObjectId):
    chapters = []
    story = await get_story(story_id)
    cur_id = story['head_chapter']
    while cur_id:
        chapter = await get_chapter(cur_id)
        summary = get_summary_from_chapter(chapter)
        chapters.append(summary)
        cur_id = chapter['succeeded_by']
    return chapters


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


async def get_chapter_summary(chapter_id: ObjectId):
    chapter = await get_chapter(chapter_id)
    return get_summary_from_chapter(chapter)

def get_summary_from_chapter(chapter):
    # TODO: Revise chapter summary structure
    summary = {
        'title':    chapter['title'],
        'id':       chapter['_id'],
    }
    return summary


async def get_all_paragraph_summaries(chapter_id: ObjectId):
    paragraphs = []
    chapter = await get_chapter(chapter_id)
    cur_id = chapter['head_paragraph']
    while cur_id:
        paragraph = await get_paragraph(cur_id)
        summary = get_summary_from_paragraph(paragraph)
        paragraphs.append(summary)
        cur_id = paragraph['succeeded_by']
    return paragraphs


async def get_remaining_chapters(chapter_id: ObjectId):
    return await get_n_succeeding_chapters(chapter_id)


async def get_n_succeeding_chapters(chpater_id: ObjectId, num_chapters=None):
    ...


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


async def get_paragraph_summary(paragraph_id: ObjectId):
    paragraph = await get_paragraph(paragraph_id)
    return get_summary_from_paragraph(paragraph)


def get_summary_from_paragraph(paragraph):
    # TODO: Revise paragraph summary strucrure
    summary = {
        'text':         paragraph['text'],
        'id':           paragraph['_id'],
        'statistics':   paragraph['statistics'],
    }
    return summary


async def get_remaining_paragraphs(paragraph_id: ObjectId):
    return await get_n_succeeding_paragraphs(paragraph_id)


async def get_n_succeeding_paragraphs(paragraph_id: ObjectId, num_paragraphs=None):
    ...


async def update_paragraphs_succeeded_by(preceding_id: ObjectId, new_paragraph_id: ObjectId):
    await _PARAGRAPHS.update_one({'_id': preceding_id}, {'$set': {'succeeded_by': new_paragraph_id}})


async def update_paragraphs_preceded_by(succeeding_id: ObjectId, new_paragraph_id: ObjectId):
    await _PARAGRAPHS.update_one({'_id': succeeding_id}, {'$set': {'preceded_by': new_paragraph_id}})


############################################################
##
## Wiki Related Methods
##
############################################################


async def get_wiki_segment(segment_id: ObjectId):
    return await _WIKI_SEGMENTS.find_one({'_id': segment_id})


async def create_wiki_page(segment_id: ObjectId, title: str):
    page = {
        'title':      title,
        'sections':   list(),
        'references': list(),
        'aliases':    list(),
    }
    result = await _WIKI_PAGES.insert_one(page)           # type: pymongo.results.InsertOneResult
    page_id = result.inserted_id
    await add_wiki_page_to_segment(segment_id, page_id)
    return page_id


async def get_wiki_page(page_id: ObjectId):
    result = await _WIKI_PAGES.find_one({'_id': page_id})
    return result


async def add_wiki_page_to_segment(segment_id: ObjectId, page_id: ObjectId):
    await _WIKI_SEGMENTS.update_one({'_id': segment_id}, {'$push': {'pages': page_id}})


async def create_wiki_section(page_id: ObjectId, title: str, preceded_by=None, succeeded_by=None):
    section = {
        'title':      title,
        'head_paragraph': None,
        'tail_paragraph': None,
        'preceded_by': preceded_by,
        'succeeded_by': succeeded_by,
    }
    result = await _WIKI_SECTIONS.insert_one(section)   # type: pymongo.results.InsertOnResult
    section_id = result.inserted_id
    await add_wiki_section_to_page(page_id, section_id)
    return section_id


async def add_wiki_section_to_page(page_id: ObjectId, section_id: ObjectId):
    await _WIKI_PAGES.insert_one({'_id': page_id}, {'$push': {'sections': section_id}})


async def get_wiki_section(section_id: ObjectId):
    result = await _WIKI_SECTIONS.find_one({'_id': section_id})
    return result


async def update_head_paragraph_of_section(section_id: ObjectId, new_head_id: ObjectId):
    await _WIKI_SECTIONS.update_one({'_id': section_id}, {'$set': {'head_paragraph': new_head_id}})


async def update_tail_paragraph_of_section(section_id: ObjectId, new_tail_id: ObjectId):
    await _WIKI_SECTIONS.update_one({'_id': section_id}, {'$set': {'tail_paragraph': new_tail_id}})


async def create_wiki_paragraph(section_id: ObjectId, text: str, preceded_by_id: ObjectId, succeeded_by_id: ObjectId):
    if preceded_by_id is None and succeeded_by_id is None:
        raise ValueError("Preceding_id and succeeding_id can not both be null.")
    preceding = await get_wiki_paragraph(preceded_by_id)
    succeeding = await get_wiki_paragraph(succeeded_by_id)
    # Wishes to create paragraph at beginning of section
    if preceding is None:
        # Check paragraph is head of section
        section = await get_wiki_section(section_id)
        if section['head_paragraph'] != succeeded_by_id or succeeding['preceded_by'] is not None:
            raise ValueError("Provided paragraph is not the head of the section.")
        # Create paragraph, update succeeding and section head
        paragraph_id = await _create_wiki_paragraph(text, preceded_by_id, succeeded_by_id)
        await update_head_paragraph_of_section(section_id, paragraph_id)
    # Wishes to create paragraph at end of section
    elif succeeding is None:
        # Check paragraph is end of section
        section = await get_wiki_section(section_id)
        if section['tail_paragraph'] != preceded_by_id or preceding['succeeded_by'] is not None:
            raise ValueError("Provided paragraph is not the tail of the section.")
        # Create paragraph, update preceding and section tail
        paragraph_id = await _create_wiki_paragraph(text, preceded_by_id, succeeded_by_id)
        await update_tail_paragraph_of_section(section_id, paragraph_id)
    # Wish to create paragraph between two paragraphs
    else:
        # Check adjacency of paragraphs
        if preceding['succeeded_by'] != succeeded_by_id or succeeding['preceded_by'] != preceded_by_id:
            raise ValueError("Provided paragraphs are not adjacent. Cannot insert between the two.")
        # Create paragraph, update surrounding paragraphs
        paragraph_id = await _create_wiki_paragraph(text, preceded_by_id, succeeded_by_id)
        await update_wiki_paragraph_preceded_by(succeeded_by_id, paragraph_id)
        await update_wiki_paragraph_succeeded_by(preceded_by_id, paragraph_id)
    return paragraph_id


async def _create_wiki_paragraph(text: str, preceded_by: ObjectId, succeeded_by: ObjectId):
    paragraph = {
        'text':         text,
        'preceded_by':  preceded_by,
        'succeeded_by': succeeded_by,
    }
    result = await _WIKI_PARAGRAPHS.insert_one(paragraph)
    paragraph_id = result.inserted_id
    return paragraph_id

async def get_wiki_paragraph(paragraph_id: ObjectId):
    result = await _WIKI_PARAGRAPHS.find_one({'_id': paragraph_id})
    return result

async def update_wiki_paragraph_succeeded_by(paragraph_id: ObjectId, succeeding_id: ObjectId):
    await _WIKI_PARAGRAPHS.update_one({'_id': paragraph_id}, {'$set': {'succeeded_by': succeeding_id}})


async def update_wiki_paragraph_preceded_by(paragraph_id: ObjectId, preceding_id: ObjectId):
    await _WIKI_PARAGRAPHS.update_one({'_id': paragraph_id}, {'$set': {'preceded_by': preceding_id}})