import sys
sys.path.append('..')

from loom import database

import asyncio
import glob
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
        chapter_id = await database.create_chapter(story_id, chapter_title, previous_chapter_id)
        previous_paragraph_id = None
        for paragraph in chapter:
            previous_paragraph_id = await database.create_paragraph(chapter_id, previous_paragraph_id, text=paragraph)
        previous_chapter_id = chapter_id
    return story_id


def find_books(bookdir):
    bookfiles = glob.glob(os.path.join(bookdir, '*.book'))
    return bookfiles


def main(bookdir, user_id, wiki_id, event_loop):
    bookfiles = find_books(bookdir)
    for bookfile in bookfiles:
        event_loop.run_until_complete(import_book(bookfile, user_id, wiki_id))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('bookdir')
    parser.add_argument('user_id')
    parser.add_argument('wiki_id')
    args = parser.parse_args()

    answer = input("This will drop your database... continue? [y/N] ")
    if answer.lower().startswith('y'):
        print("Continuing.")
        event_loop = asyncio.get_event_loop()
        # database.drop_database()
        # event_loop.run_until_complete(database.drop_database())
        main(args.bookdir, args.user_id, args.wiki_id, event_loop)
        event_loop.close()
    else:
        print("Quitting...")
