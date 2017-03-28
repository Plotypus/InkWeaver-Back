from .abstract_interface import AbstractDBInterface

from loom.database.clients import *
from loom.serialize import decode_string_to_bson, encode_bson_to_string

import nltk
import re

from bson.objectid import ObjectId
from collections import Counter, defaultdict
from itertools import chain
from os.path import dirname, join as pathjoin
from string import punctuation
from typing import ClassVar

# Adjust the NLTK path.
nltk.data.path.insert(0, pathjoin(dirname(dirname(dirname(__file__))), 'nltk_data'))

CREATE_LINK_REGEX = re.compile(r'{#\|(.*?)\|#}')

def generate_link_format_regex():
    o = ObjectId()
    inner_regex = r'[a-f\d]{24}'
    bson_string = encode_bson_to_string(o)
    # TODO: Temporary fix.
    # Strip the whitespace in the encoding and allow one or more spaces.
    # Note: re.escape also escapes spaces, which is why the replace looks for '\\ '.
    pattern = re.escape(bson_string).replace(str(o), inner_regex).replace('\\ ', r'\s*')
    return re.compile(pattern)


class InterfaceError(Exception):
    def __init__(self, message: str, *, query: str):
        self.message = message
        self.query = query


class BadValueError(InterfaceError):
    def __init__(self, *, query: str, value):
        super().__init__('bad value supplied', query=query)
        self.value = value


class FailedUpdateError(InterfaceError):
    def __init__(self, *, query: str):
        super().__init__('unable to complete update', query=query)


class MongoDBInterface(AbstractDBInterface):
    def __init__(self, db_client_class: ClassVar, db_name, db_host, db_port, db_user=None, db_pass=None):
        if not issubclass(db_client_class, MongoDBClient):
            raise ValueError("invalid MongoDB client class: {}".format(db_client_class.__name__))  # pragma: no cover
        self._client = db_client_class(db_name, db_host, db_port, db_user, db_pass)
        self._link_format_regex = generate_link_format_regex()

    @property
    def client(self) -> MongoDBClient:
        return self._client

    @property
    def host(self):
        return self.client.host

    @property
    def port(self):
        return self.client.port

    @property
    def link_format_regex(self):
        return self._link_format_regex

    ###########################################################################
    #
    # Database Methods
    #
    ###########################################################################

    async def authenticate_client(self, username, password):
        await self.client.authenticate(username, password)

    async def drop_database(self):
        await self.client.drop_database()

    async def drop_all_collections(self):
        await self.client.drop_all_collections()

    ###########################################################################
    #
    # User Methods
    #
    ###########################################################################

    async def create_user(self, username, password, name, email, bio=None):
        if await self.client.username_exists(username):
            raise ValueError('Username is already taken.')
        if await self.client.email_exists(email):
            raise ValueError('Email is already taken.')
        password_hash = super().hash_password(password)
        inserted_id = await self.client.create_user(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            bio=bio,
            avatar=None
        )
        return inserted_id

    async def password_is_valid_for_username(self, username, password):
        try:
            stored_hash = await self.client.get_password_hash_for_username(username)
        except NoMatchError:
            return False
        else:
            return super().verify_hash(password, stored_hash)

    async def get_user_id_for_username(self, username):
        user_id = await self.client.get_user_id_for_username(username)
        return user_id

    async def get_user_preferences(self, user_id):
        preferences = await self.client.get_user_preferences(user_id)
        return preferences

    async def get_user_stories_and_wikis(self, user_id):
        story_ids_and_positions = await self.client.get_user_stories(user_id)
        wiki_ids = await self.client.get_user_wiki_ids(user_id)
        wiki_ids_to_titles = {}
        wikis = []
        for wiki_id in wiki_ids:
            wiki = await self.client.get_wiki(wiki_id)
            wiki_ids_to_titles[wiki_id] = wiki['title']
            access_level = self._get_current_user_access_level_in_object(user_id, wiki)
            wikis.append({
                'wiki_id':      wiki_id,
                'title':        wiki['title'],
                'access_level': access_level,
            })
        stories = []
        for story_id_and_pos in story_ids_and_positions:
            story_id = story_id_and_pos['story_id']
            last_pos = story_id_and_pos['position_context']
            story = await self.client.get_story(story_id)
            access_level = self._get_current_user_access_level_in_object(user_id, story)
            wiki_title = wiki_ids_to_titles[story['wiki_id']]
            stories.append({
                'story_id': story_id,
                'title': story['title'],
                'wiki_summary': {'wiki_id': story['wiki_id'], 'title': wiki_title},
                'access_level': access_level,
                'position_context': last_pos,
            })
        return {'stories': stories, 'wikis': wikis}

    @staticmethod
    def _get_current_user_access_level_in_object(user_id, obj):
        for user in obj['users']:
            if user['user_id'] == user_id:
                return user['access_level']

    async def set_user_password(self, user_id, password):
        # TODO: Check the password is not equal to the previous password.
        # Maybe even check that it's not too similar, like:
        #   https://security.stackexchange.com/questions/53481/does-facebook-store-plain-text-passwords
        password_hash = super().hash_password(password)
        await self.client.set_user_password_hash(user_id, password_hash)

    async def set_user_name(self, user_id, name):
        await self.client.set_user_name(user_id, name)

    async def set_user_email(self, user_id, email):
        await self.client.set_user_email(user_id, email)

    async def set_user_bio(self, user_id, bio):
        await self.client.set_user_bio(user_id, bio)

    async def set_user_avatar(self, user_id, avatar):
        await self.client.set_user_avatar(user_id, avatar)

    async def set_story_position_context(self, user_id, story_id, position_context):
        await self.client.set_user_story_position_context(user_id, story_id, position_context)

    ###########################################################################
    #
    # Story Methods
    #
    ###########################################################################

    async def create_story(self, user_id, title, summary, wiki_id) -> ObjectId:
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        section_id = await self.create_section(title)
        await self.add_paragraph(section_id, summary)
        inserted_id = await self.client.create_story(title, wiki_id, user_description, section_id)
        await self.client.add_story_to_user(user_id, inserted_id)
        return inserted_id

    async def create_section(self, title) -> ObjectId:
        inserted_id = await self.client.create_section(title)
        return inserted_id

    async def add_preceding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_preceding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_inner_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_inner_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_succeeding_subsection(self, title, parent_id, index=None):
        subsection_id = await self.create_section(title)
        try:
            await self.client.insert_succeeding_subsection(subsection_id, to_section_id=parent_id, at_index=index)
        except ClientError:
            await self.delete_section(subsection_id)
        else:
            return subsection_id

    async def add_paragraph(self, section_id, text, succeeding_paragraph_id=None):
        try:
            if not succeeding_paragraph_id:
                index = None
            else:
                paragraph_ids = await self.client.get_paragraph_ids(section_id)
                index = paragraph_ids.index(succeeding_paragraph_id)
        except ValueError:
            raise BadValueError(query='add_paragraph', value=succeeding_paragraph_id)
        else:
            paragraph_id = ObjectId()
            await self.client.insert_paragraph(paragraph_id, '', to_section_id=section_id, at_index=index)
            await self.client.insert_links_for_paragraph(paragraph_id, list(), in_section_id=section_id, at_index=index)
            # Default the note to None
            await self.client.insert_note_for_paragraph(paragraph_id, None, in_section_id=section_id, at_index=index)
            if text is not None:
                links_created = await self.set_paragraph_text(section_id, text, paragraph_id)
            else:
                links_created = []
            return paragraph_id, links_created

    async def add_bookmark(self, name, story_id, section_id, paragraph_id, index=None):
        bookmark_id = ObjectId()
        await self.client.insert_bookmark(bookmark_id, story_id, section_id, paragraph_id, name, index)
        return bookmark_id

    async def get_story(self, story_id):
        story = await self.client.get_story(story_id)
        return story

    async def get_story_bookmarks(self, story_id):
        story = await self.client.get_story(story_id)
        return story['bookmarks']

    async def get_story_hierarchy(self, story_id):
        story = await self.get_story(story_id)
        section_id = story['section_id']
        return await self.get_section_hierarchy(section_id)

    async def get_section_hierarchy(self, section_id):
        section = await self.client.get_section(section_id)
        hierarchy = {
            'title':      section['title'],
            'section_id': section_id,
            'preceding_subsections':
                [await self.get_section_hierarchy(pre_sec_id) for pre_sec_id in section['preceding_subsections']],
            'inner_subsections':
                [await self.get_section_hierarchy(sec_id) for sec_id in section['inner_subsections']],
            'succeeding_subsections':
                [await self.get_section_hierarchy(post_sec_id) for post_sec_id in section['succeeding_subsections']],
        }
        return hierarchy

    async def get_section_content(self, section_id):
        section = await self.client.get_section(section_id)
        paragraphs = []
        for db_paragraph, db_note in zip(section['content'], section['notes']):
            def join_dictionaries_and_return(paragraph, note):
                paragraph.update(note)
                return paragraph
            paragraphs.append(join_dictionaries_and_return(db_paragraph, db_note))
        return paragraphs

    async def set_story_title(self, story_id, title):
        story = await self.client.get_story(story_id)
        try:
            await self.client.set_story_title(story_id, title)
            await self.client.set_section_title(story['section_id'], title)
        except ClientError:
            raise FailedUpdateError(query='set_story_title')
        else:
            # TODO: Should this return something?
            pass

    async def set_section_title(self, section_id, title):
        await self.client.set_section_title(section_id, title)

    async def set_paragraph_text(self, section_id, text, paragraph_id):
        text, links_created = await self._find_and_create_links_in_paragraph(section_id, paragraph_id, text)
        sentences_and_links, word_frequencies = await self.get_links_and_word_counts_from_paragraph(text)
        page_updates = {}
        section_links = []
        for sentence, links in sentences_and_links:
            for link in links:
                link_id = link['_id']
                context = link['context']
                context['paragraph_id'] = paragraph_id
                context['text'] = sentence
                # Update context in link.
                await self.client.set_link_context(link_id, context)
                # Get page ID from link and add its context to `page_updates`.
                page_id = link['page_id']
                link_updates = page_updates.get(page_id)
                if link_updates is None:
                    link_updates = {}
                    page_updates[page_id] = link_updates
                link_updates[link_id] = context
                # Add link to `section_links` to update the links for the paragraph.
                section_links.append(link_id)
        # Apply updates to references in pages.
        for page_id, updates in page_updates.items():
            page = await self.client.get_page(page_id)
            references = page['references']
            for link_id, context in updates.items():
                self._update_link_in_references_with_context(references, link_id, context)
            await self.client.set_page_references(page_id, references)
        # Update links for this paragraph for the section.
        await self.client.set_links_in_section(section_id, section_links, paragraph_id)
        await self.client.set_paragraph_text(paragraph_id, text, in_section_id=section_id)
        # Get statistics for section and paragraph
        section_stats = await self.client.get_section_statistics(section_id)
        section_wf = Counter(section_stats['word_frequency'])
        paragraph_stats = await self.client.get_paragraph_statistics(section_id, paragraph_id)
        paragraph_wf = Counter(paragraph_stats['word_frequency'])
        # Update statistics for section and paragraph
        section_wf.subtract(paragraph_wf)
        section_wf.update(word_frequencies)
        await self.client.set_section_statistics(section_id, section_wf, sum(section_wf.values()))
        await self.client.set_paragraph_statistics(paragraph_id, word_frequencies, sum(word_frequencies.values()),
                                                   section_id)
        return links_created

    @staticmethod
    def _update_link_in_references_with_context(references, link_id, context):
        for reference in references:
            if reference['link_id'] == link_id:
                reference['context'] = context
                break

    async def get_links_and_word_counts_from_paragraph(self, paragraph_text):
        # TODO: Support languages other than English.
        sentences = nltk.sent_tokenize(paragraph_text)
        word_counts = Counter()
        results = []
        for sentence in sentences:
            sentence_links = []
            links_replaced_sentence = sentence
            link_matches = re.findall(self.link_format_regex, sentence)
            for match in link_matches:
                potential_id = decode_string_to_bson(match)
                link = await self.get_link(potential_id)
                if link is not None:
                    alias = await self.client.get_alias(link['alias_id'])
                    replacement = alias['name']
                    links_replaced_sentence = links_replaced_sentence.replace(match, replacement)
                    sentence_links.append(link)
            # Mongo does not support '$' or '.' in key name, so we replace them with their unicode equivalents.
            words = [token.replace('.', '').replace('$', '').lower() for token in
                     nltk.word_tokenize(links_replaced_sentence) if token not in punctuation]
            word_counts.update(words)
            if sentence_links:
                sentence_tuple = (sentence, sentence_links)
                results.append(sentence_tuple)
        return results, word_counts

    async def _find_and_create_links_in_paragraph(self, section_id, paragraph_id, text):
        prev_end = 0
        links_created = []  # (link_id, page_id, name)
        # Buffer used for efficiently joining the string back together.
        buffer = []
        # Iterate through each encoded request and replace with a link_id.
        for match in CREATE_LINK_REGEX.finditer(text):
            start, end = match.span()
            link_id, page_id, name = await self._create_link_and_replace_text(section_id, paragraph_id, text,
                                                                              start, end)
            links_created.append((link_id, page_id, name))
            # Strip out the space in the encoding.
            encoded_link_id = encode_bson_to_string(link_id).replace(' ', '')
            # Add the previous text and link_id to the buffer.
            buffer.append(text[prev_end:start])
            buffer.append(encoded_link_id)
            prev_end = end
        # Don't forget to add the rest of the string.
        buffer.append(text[prev_end:])
        return ''.join(buffer), links_created

    async def _create_link_and_replace_text(self, section_id, paragraph_id, text, start, end):
        # Get the match and split it into story_id, page_id, and name.
        tokens = text[start:end].split('|')[1:4]
        story_id, page_id, name = tuple(tokens)
        # Convert oids from strings to ObjectId.
        story_id = decode_string_to_bson(story_id)
        page_id = decode_string_to_bson(page_id)
        link_id = await self.create_link(story_id, section_id, paragraph_id, name, page_id)
        return link_id, page_id, name

    async def set_bookmark_name(self, story_id, bookmark_id, new_name):
        await self.client.set_bookmark_name(story_id, bookmark_id, new_name)

    async def set_note(self, section_id, paragraph_id, text):
        await self.client.set_note(section_id, paragraph_id, text)

    async def delete_story(self, story_id):
        story = await self.get_story(story_id)
        section_id = story['section_id']
        await self.recur_delete_section_and_subsections(section_id)
        for user in story['users']:
            user_id = user['user_id']
            await self.client.remove_story_from_user(user_id, story_id)
        await self.client.delete_story(story_id)

    async def delete_section(self, section_id):
        await self.recur_delete_section_and_subsections(section_id)

    async def recur_delete_section_and_subsections(self, section_id):
        section = await self.client.get_section(section_id)
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            await self.recur_delete_section_and_subsections(subsection_id)
        for link_summary in section['links']:
            link_ids = link_summary['links']
            for link_id in link_ids:
                await self.delete_link(link_id)
        await self.client.delete_section(section['_id'])
        await self.client.delete_bookmark_by_section_id(section_id)

    async def delete_paragraph(self, section_id, paragraph_id):
        link_ids = await self.client.get_links_in_paragraph(paragraph_id, section_id)
        for link_id in link_ids:
            await self.delete_link(link_id)
        await self.client.delete_paragraph(section_id, paragraph_id)
        await self.client.delete_bookmark_by_paragraph_id(paragraph_id)

    async def delete_note(self, section_id, paragraph_id):
        # To delete a note, we simply set it as an empty-string.
        await self.client.set_note(section_id, paragraph_id, '')

    async def delete_bookmark(self, bookmark_id):
        await self.client.delete_bookmark_by_id(bookmark_id)

    async def move_subsection_as_preceding(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise ValueError
        try:
            await self.client.remove_section_from_parent(section_id)
            await self.client.insert_preceding_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_preceding')

    async def move_subsection_as_inner(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise ValueError
        try:
            await self.client.remove_section_from_parent(section_id)
            await self.client.insert_inner_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_inner')

    async def move_subsection_as_succeeding(self, section_id, to_parent_id, to_index):
        if await self._section_is_ancestor_of_candidate(section_id, to_parent_id):
            raise ValueError
        try:
            await self.client.remove_section_from_parent(section_id)
            await self.client.insert_succeeding_subsection(section_id, to_section_id=to_parent_id, at_index=to_index)
        except ClientError:
            raise FailedUpdateError(query='move_subsection_as_succeeding')

    async def _section_is_ancestor_of_candidate(self, section_id, candidate_section_id):
        if section_id == candidate_section_id:
            return True
        section = await self.client.get_section(section_id)
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            if await self._section_is_ancestor_of_candidate(subsection_id, candidate_section_id):
                return True
        return False

    ###########################################################################
    #
    # Wiki Methods
    #
    ###########################################################################

    async def create_wiki(self, user_id, title, summary):
        user = await self.get_user_preferences(user_id)
        user_description = {
            'user_id':      user_id,
            'name':         user['name'],
            'access_level': 'owner',
        }
        segment_id = await self.create_segment(title)
        inserted_id = await self.client.create_wiki(title, user_description, summary, segment_id)
        await self.client.add_wiki_to_user(user_id, inserted_id)
        return inserted_id

    async def create_segment(self, title):
        inserted_id = await self.client.create_segment(title)
        return inserted_id

    async def create_page(self, title, in_parent_segment):
        # Create the page and include the `template_headings` from the parent
        parent_segment = await self.get_segment(in_parent_segment)
        template_headings = parent_segment['template_headings']
        page_id = await self.client.create_page(title, template_headings)
        # Create an alias for the page with the title as the alias name
        await self._create_alias(page_id, title)
        try:
            await self.client.append_page_to_parent_segment(page_id, in_parent_segment)
        except ClientError:
            await self.delete_page(page_id)
        else:
            return page_id

    async def add_child_segment(self, title, parent_id):
        parent_segment = await self.client.get_segment(parent_id)
        template_headings = parent_segment['template_headings']
        child_segment_id = await self.client.create_segment(title, template_headings)
        try:
            await self.client.append_segment_to_parent_segment(child_segment_id, parent_id)
        except ClientError:
            await self.delete_segment(child_segment_id)
        else:
            return child_segment_id

    async def add_template_heading(self, title, segment_id):
        heading = await self.client.get_template_heading(title, segment_id)
        # Template heading already exists within the segment
        if heading is not None:
            # TODO: Deal with this
            return
        try:
            await self.client.append_template_heading_to_segment(title, segment_id)
        except ClientError:
            raise FailedUpdateError(query='add_template_heading')
        else:
            # TODO: Should this return something?
            pass

    async def add_heading(self, title, page_id, index=None):
        heading = await self.client.get_heading(title, page_id)
        # Heading already exists within the page
        if heading is not None:
            # TODO: Deal with this
            return
        try:
            await self.client.insert_heading(title, page_id, index)
        except ClientError:
            raise FailedUpdateError(query='add_heading')
        else:
            # TODO: Should this return something?
            pass

    async def get_wiki(self, wiki_id):
        wiki = await self.client.get_wiki(wiki_id)
        return wiki

    async def get_wiki_alias_list(self, wiki_id):
        wiki = await self.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self._get_segment_alias_list(segment_id)

    async def _get_segment_alias_list(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        # Get all the alias information for the pages at the current level.
        segment_alias_list = []
        for page_id in segment['pages']:
            for alias_entry in await self._get_page_alias_list(page_id):
                segment_alias_list.append(alias_entry)
        # Then add all child segments' page alias lists to the current list, keeping it flat.
        for segment_id in segment['segments']:
            for page_aliases in await self._get_segment_alias_list(segment_id):
                segment_alias_list.append(page_aliases)
        return segment_alias_list

    async def _get_page_alias_list(self, page_id):
        page = await self.client.get_page(page_id)
        alias_list = []
        for alias_name, alias_id in page['aliases'].items():
            alias = await self.client.get_alias(alias_id)
            alias_list.append({
                'alias_name':   alias_name,
                'page_id':      page_id,
                'link_ids':     alias['links'],
            })
        return alias_list

    async def get_wiki_hierarchy(self, wiki_id):
        wiki = await self.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self.get_segment_hierarchy(segment_id)

    async def get_segment_hierarchy(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        hierarchy = {
            'title':      segment['title'],
            'segment_id': segment_id,
            'segments':   [],
            'pages':      [],
        }
        segments = hierarchy['segments']
        pages = hierarchy['pages']
        # Iterate through the segments, popping out the `links` field and inserting them into the top-level `links`.
        for segment_id in segment['segments']:
            inner_segment = await self.get_segment_hierarchy(segment_id)
            segments.append(inner_segment)
        # Iterate through the pages, pulling the links from the aliases inside of each.
        for page_id in segment['pages']:
            page = await self._get_page_for_hierarchy(page_id)
            pages.append(page)
        return hierarchy

    async def _get_page_for_hierarchy(self, page_id):
        page = await self.client.get_page(page_id)
        return {
            'title':   page['title'],
            'page_id': page_id,
        }

    async def get_segment(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        segment['segments'] = [await self.get_segment_summary(child_id) for child_id in segment['segments']]
        segment['pages'] = [await self.get_page_summary(page_id) for page_id in segment['pages']]
        return segment

    async def get_segment_summary(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        return {
            'segment_id': segment_id,
            'title':      segment['title'],
        }

    async def get_page(self, page_id):
        page = await self.client.get_page(page_id)
        for reference in page['references']:
            # Take the context from inside the reference and push it to the next level up.
            reference.update(reference.pop('context'))
        return page

    async def get_page_summary(self, page_id):
        page = await self.client.get_page(page_id)
        return {
            'page_id':   page_id,
            'title':     page['title'],
        }

    async def get_heading(self, heading_id):
        # TODO: Do this.
        pass

    async def set_wiki_title(self, title, wiki_id):
        wiki = await self.client.get_wiki(wiki_id)
        try:
            await self.client.set_wiki_title(title, wiki_id)
            await self.client.set_segment_title(title, wiki['segment_id'])
        except ClientError:
            raise FailedUpdateError(query='set_wiki_title')
        else:
            # TODO: Should this return something?
            pass

    async def set_segment_title(self, title, segment_id):
        try:
            await self.client.set_segment_title(title, segment_id)
        except ClientError:
            raise FailedUpdateError(query='set_segment_title')
        else:
            # TODO: Should this return something?
            pass

    async def set_template_heading_title(self, old_title, new_title, segment_id):
        try:
            await self.client.set_template_heading_title(old_title, new_title, segment_id)
        except ClientError:
            raise
        else:
            pass

    async def set_template_heading_text(self, title, text, segment_id):
        try:
            await self.client.set_template_heading_text(title, text, segment_id)
        except ClientError:
            raise
        else:
            pass

    async def set_page_title(self, new_title, page_id):
        page = await self.client.get_page(page_id)
        old_title = page['title']
        alias_id = page['aliases'][old_title]
        # It's important that we change the page title before renaming the alias
        # Otherwise, we are going to keep creating new aliases
        await self.client.set_page_title(new_title, page_id)
        await self.change_alias_name(alias_id, new_title)

    async def set_heading_title(self, old_title, new_title, page_id):
        heading = await self.client.get_heading(new_title, page_id)
        # Heading already exists within the page
        if heading is not None:
            # TODO: Deal with this
            return
        try:
            await self.client.set_heading_title(old_title, new_title, page_id)
        except ClientError:
            raise FailedUpdateError(query='set_heading_title')
        else:
            # TODO: Should this return something?
            pass

    async def set_heading_text(self, title, text, page_id):
        try:
            await self.client.set_heading_text(title, text, page_id)
        except ClientError:
            raise FailedUpdateError(query='set_heading_text')
        else:
            # TODO: Should this return something?
            pass

    async def delete_wiki(self, user_id, wiki_id):
        # TODO: Is this the best way to handle this? Should all stories use one new wiki? Should this be an option?
        wiki = await self.client.get_wiki(wiki_id)
        # Update each story using this wiki with a new wiki.
        story_summaries = await self.client.get_summaries_of_stories_using_wiki(wiki_id)
        for summary in story_summaries:
            story_id = summary['_id']
            title = summary['title']
            wiki_title = f"{title} Wiki"
            wiki_summary = f"A wiki for {title}."
            # Create the new wiki and set it for the story.
            new_wiki_id = await self.create_wiki(user_id, wiki_title, wiki_summary)
            await self.client.set_story_wiki(story_id, new_wiki_id)
        # Recursively delete all segments in the wiki.
        segment_id = wiki['segment_id']
        deleted_link_ids = await self.delete_segment(segment_id)
        # Delete the wiki proper.
        await self.client.delete_wiki(wiki_id)
        return deleted_link_ids

    async def delete_segment(self, segment_id):
        deleted_link_ids = await self.recur_delete_segment_and_subsegments(segment_id)
        return deleted_link_ids

    async def recur_delete_segment_and_subsegments(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        deleted_link_ids = []
        for subsegment_id in segment['segments']:
            segment_deleted_link_ids = await self.recur_delete_segment_and_subsegments(subsegment_id)
            deleted_link_ids.extend(segment_deleted_link_ids)
        for page_id in segment['pages']:
            page_deleted_link_ids = await self.delete_page(page_id)
            deleted_link_ids.extend(page_deleted_link_ids)
        await self.client.delete_segment(segment_id)
        return deleted_link_ids

    async def delete_template_heading(self, title, segment_id):
        try:
            await self.client.delete_template_heading(title, segment_id)
        except ClientError:
            raise
        else:
            pass

    async def delete_page(self, page_id):
        page = await self.client.get_page(page_id)
        deleted_link_ids = []
        for alias_id in page['aliases'].values():
            page_deleted_link_ids = await self._delete_alias_no_replace(alias_id)
            deleted_link_ids.extend(page_deleted_link_ids)
        await self.client.delete_page(page_id)
        return deleted_link_ids

    async def delete_heading(self, heading_title: str, page_id: ObjectId):
        await self.client.delete_heading(heading_title, page_id)

    ###########################################################################
    #
    # Link Methods
    #
    ###########################################################################

    async def create_link(self, story_id: ObjectId, section_id: ObjectId, paragraph_id: ObjectId, name: str,
                          page_id: ObjectId):
        # Check if alias exists.
        alias_id = await self.client.find_alias_in_page(page_id, name)
        if alias_id is None:
            # Create a new alias and add it to the page.
            alias_id = await self._create_alias(page_id, name)
        # Now create a link with the alias.
        link_id = await self.client.create_link(alias_id, page_id, story_id, section_id, paragraph_id)
        await self.client.insert_link_to_alias(link_id, alias_id)
        # Insert the reference into the appropriate page.
        await self.client.insert_reference_to_page(page_id, link_id, story_id, section_id, paragraph_id)
        return link_id

    async def get_link(self, link_id):
        return await self.client.get_link(link_id)

    async def delete_link(self, link_id):
        # TODO: Should an alias be deleted if no more links are tied to it?
        link = await self.get_link(link_id)
        alias_id = link['alias_id']
        page_id = link['page_id']
        await self.client.remove_link_from_alias(link_id, alias_id)
        await self.client.remove_reference_from_page(link_id, page_id)
        await self.client.delete_link(link_id)

    async def comprehensive_remove_link(self, link_id: ObjectId, replacement_text: str):
        link = await self.get_link(link_id)
        context = link['context']
        text = await self.client.get_paragraph_text(context['section_id'], context['paragraph_id'])
        # TODO: Updated link encoding -> need to update here.
        serialized_link = encode_bson_to_string(link_id).replace(' ', '')
        updated_text = text.replace(serialized_link, replacement_text)
        await self.set_paragraph_text(context['section_id'], updated_text, context['paragraph_id'])
        await self.delete_link(link_id)

    ###########################################################################
    #
    # Alias Methods
    #
    ###########################################################################

    async def change_alias_name(self, alias_id: ObjectId, new_name: str):
        # Update name in alias.
        alias = await self.client.get_alias(alias_id)
        page_id = alias['page_id']
        old_name = alias['name']
        await self.client.set_alias_name(new_name, alias_id)
        # Update `aliases` in the appropriate page.
        await self.client.update_alias_name_in_page(page_id, old_name, new_name)
        page = await self.client.get_page(page_id)
        # Alias with page title renamed, need to recreate primary alias
        if not await self._page_title_is_alias(page):
            # TODO: Or do we rename the page here as well?
            await self._create_alias(page_id, old_name)

    async def get_alias(self, alias_id: ObjectId):
        return await self.client.get_alias(alias_id)

    async def delete_alias(self, alias_id: ObjectId):
        alias = await self.get_alias(alias_id)
        deleted_link_ids = await self._delete_alias_no_replace(alias_id)
        alias_name = alias['name']
        page_id = alias['page_id']
        page = await self.client.get_page(page_id)
        # Alias with page title deleted, need to recreate primary alias
        if page is not None and not await self._page_title_is_alias(page):
            await self._create_alias(page_id, alias_name)
        return deleted_link_ids

    async def _delete_alias_no_replace(self, alias_id: ObjectId):
        alias = await self.get_alias(alias_id)
        alias_name = alias['name']
        for link_id in alias['links']:
            await self.comprehensive_remove_link(link_id, alias_name)
        page_id = alias['page_id']
        await self.client.remove_alias_from_page(alias_name, page_id)
        await self.client.delete_alias(alias_id)
        return alias['links']

    async def _create_alias(self, page_id: ObjectId, name: str):
        alias_id = await self.client.create_alias(name, page_id)
        await self.client.insert_alias_to_page(page_id, name, alias_id)
        return alias_id

    async def _page_title_is_alias(self, page):
        title = page['title']
        return page['aliases'].get(title) is not None

    ###########################################################################
    #
    # Statistics Methods
    #
    ###########################################################################

    async def get_story_statistics(self, story_id):
        story = await self.client.get_story(story_id)
        stats = await self._recur_get_section_statistics(story['section_id'])
        return stats

    async def _recur_get_section_statistics(self, section_id):
        section = await self.client.get_section(section_id)
        word_freqs = Counter(section['statistics']['word_frequency'])
        for subsection_id in chain(section['preceding_subsections'],
                                   section['inner_subsections'],
                                   section['succeeding_subsections']):
            subsection_stats = await self._recur_get_section_statistics(subsection_id)
            word_freqs.update(subsection_stats['word_frequency'])
            section['statistics']['word_frequency'] = word_freqs
            section['statistics']['word_count'] += subsection_stats['word_count']
        return section['statistics']

    async def get_section_statistics(self, section_id):
        return await self._recur_get_section_statistics(section_id)

    async def get_paragraph_statistics(self, section_id, paragraph_id):
        return await self.client.get_paragraph_statistics(section_id, paragraph_id)

    async def get_page_frequencies_in_story(self, story_id, wiki_id):
        wiki = await self.client.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self._get_page_section_frequencies(story_id, segment_id)

    async def _get_page_section_frequencies(self, story_id, segment_id):
        segment = await self.client.get_segment(segment_id)
        pages = []
        for page_id in segment['pages']:
            page = await self.get_page(page_id)
            frequencies = defaultdict(int)
            for reference in filter(lambda ref: ref['story_id'] == story_id, page['references']):
                key = encode_bson_to_string(reference['section_id'])
                frequencies[key] += 1
            pages.append({'page_id': page_id, 'section_frequencies': frequencies})
        for child_segment_id in segment['segments']:
            child_pages = await self._get_page_section_frequencies(story_id, child_segment_id)
            pages.extend(child_pages)
        return pages


class MongoDBTornadoInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorTornadoClient, db_name, db_host, db_port, db_user, db_pass)


class MongoDBAsyncioInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorAsyncioClient, db_name, db_host, db_port, db_user, db_pass)
