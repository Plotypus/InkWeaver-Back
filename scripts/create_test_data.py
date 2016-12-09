import sys
sys.path.append('..')

from loom import database

import asyncio
import glob
import json
import motor.motor_asyncio
import os.path
import re


def read_book(bookfile):
    title = os.path.splitext(os.path.basename(bookfile))[0]
    with open(bookfile) as f:
        lines = f.readlines()
    newline = re.compile(r'([^\n])\n([^\n])')
    chapter_re = re.compile(r'^# (?P<title>.*)$')
    text = ''.join(lines)
    text = newline.sub(r'\1 \2', text)
    text = text.replace('  ', ' ')
    paragraphs = [line.replace('\n', '') for line in text.split('\n\n')]
    chapters = []
    chapter_titles = []
    if not chapter_re.fullmatch(paragraphs[0]):
        raise ValueError("Book format invalid.")
    for paragraph in paragraphs:
        match = chapter_re.fullmatch(paragraph)
        if match is not None:
            chapters.append(list())
            chapter_titles.append(match.group('title'))
        else:
            chapters[-1].append(paragraph)
    return (title, chapter_titles, chapters)


async def import_book(bookfile, user_id, wiki_id):
    title, chapter_titles, chapters = read_book(bookfile)
    story_id = await database.create_story(user_id, wiki_id, title, None)
    previous_chapter_id = None
    for i in range(len(chapters)):
        chapter_title = chapter_titles[i]
        chapter = chapters[i]
        chapter_id = await database.create_chapter(story_id, chapter_title, previous_chapter_id, None)
        previous_paragraph_id = None
        for paragraph in chapter:
            previous_paragraph_id = await database.create_paragraph(chapter_id, paragraph, previous_paragraph_id, None)
        previous_chapter_id = chapter_id
    return story_id


def find_books(bookdir):
    bookfiles = glob.glob(os.path.join(bookdir, '*.book'))
    return bookfiles


async def process_datafile(jsonfile):
    with open(jsonfile) as jf:
        data = json.load(jf)
    if not isinstance(data, list):
        raise ValueError("Invalid JSON data: {}".format(jsonfile))

    ids = {}
    first_user = None
    first_wiki = None
    # TODO: Allow dynamic default value setting (e.g. automatically assign "default_user_1", etc.)
    for obj in data:
        datatype    = obj['datatype']
        identifier  = obj['identifier']
        values      = obj['values']
        template = re.compile(r'^\{\{([^\}]+)\}\}$')
        for key, value in values.items():
            if not value:
                continue
            match = template.match(value)
            if match is not None:
                val = match.group(1)
                db_id = ids.get(val)
                if db_id is not None:
                    values[key] = db_id
                else:
                    print("No corresponding database ID for identifier: {}".format(val))
        if datatype == 'default_user':
            user_id = await database.create_default_user(**values)
            ids[identifier] = user_id
            if first_user is None:
                first_user = user_id
        elif datatype == 'user':
            user_id = await database.create_user(**values)
            print("Created user: {}".format(user_id))
            ids[identifier] = user_id
            if first_user is None:
                first_user = user_id
        elif datatype == 'wiki_root':
            root_id = await database.create_wiki_root(**values)
            print("Created wiki root: {}".format(root_id))
            ids[identifier] = root_id
            if first_wiki is None:
                first_wiki = root_id
        elif datatype == 'wiki_segment':
            segment_id = await database.create_wiki_segment(**values)
            print("Created wiki segment: {}".format(segment_id))
            ids[identifier] = segment_id
        elif datatype == 'wiki_page':
            page_id = await database.create_wiki_page(**values)
            print("Created wiki page: {}".format(page_id))
            ids[identifier] = page_id
        elif datatype == 'wiki_section':
            section_id = await database.create_wiki_section(**values)
            print("Created wiki section: {}".format(section_id))
            ids[identifier] = section_id
        elif datatype == 'wiki_paragraph':
            paragraph_id = await database.create_wiki_paragraph(**values)
            print("Created wiki paragraph: {}".format(paragraph_id))
            ids[identifier] = paragraph_id
        else:
            raise ValueError("Unsupported datatype: {}".format(datatype))
    return first_user, first_wiki


def main(jsonfile, bookdir):
    answer = input("This will drop your database... continue? [y/N] ")
    if not answer.lower().startswith('y'):
        print("Quitting...")
        return
    print("Continuing.")
    database.use_asyncio()

    event_loop = asyncio.get_event_loop()

    event_loop.run_until_complete(database.drop_database())

    user_id, wiki_id = event_loop.run_until_complete(process_datafile(jsonfile))

    bookfiles = find_books(bookdir)
    for bookfile in bookfiles:
        event_loop.run_until_complete(import_book(bookfile, user_id, wiki_id))

    event_loop.close()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data')
    parser.add_argument('bookdir')
    args = parser.parse_args()

    main(args.data, args.bookdir)
