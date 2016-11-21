from . import handlers

# User ID
RE_ObjectID = r'([a-fA-F0-9]{24})'

# Endpoints
API         = r'/api'
USER        = API       + r'/{user_id}'.format(user_id=RE_ObjectID)
STORIES     = USER      + r'/stories'
STORY       = STORIES   + r'/{story_id}'.format(story_id=RE_ObjectID)
CHAPTER     = STORY     + r'/{chapter_id}'.format(chapter_id=RE_ObjectID)
PARAGRAPH   = CHAPTER   + r'/{paragraph_id}'.format(paragraph_id=RE_ObjectID)
WIKIS       = USER      + r'/wikis'
WIKI        = WIKIS     + r'/{wiki_id}'.format(wiki_id=RE_ObjectID)
PAGE        = WIKI      + r'/{page_id}'.format(page_id=RE_ObjectID)

ROUTES = [
    (r'/ws', handlers.websockets.EchoHandler),
    (API, handlers.rest.RedirectHandler, dict(url='http://plotypus.github.io/api')),  # GET: redirect to plotypus.github.io/api
    (USER, ...),   # GET: user information
    (STORIES, handlers.rest.story.StoriesHandler),  # GET: list of user's stories; POST: create new story
    (STORY, handlers.rest.story.StoryHandler),  # GET: story content & list of chapters; POST: new chapter
    (CHAPTER, handlers.rest.story.ChapterHandler),  # GET: chapter content & list of paragraphs; POST: new paragraph
    (PARAGRAPH, handlers.rest.story.ParagraphHandler),  # GET: N/A
    (WIKIS, ...),  # GET: list of user's wikis; POST: create new wiki
    (WIKI, ...),  # GET: wiki information; POST: create new wiki page
    (PAGE, ...),  # GET: retrieve information about the page; POST: write to the page
]
