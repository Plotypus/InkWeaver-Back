from .abstract_interface import AbstractDBInterface

from loom.database.clients import *
from loom.serialize import encode_bson_to_string

import nltk
import re

from bson.objectid import ObjectId
from itertools import chain
from os.path import dirname, join as pathjoin
from typing import ClassVar

# Adjust the NLTK path.
nltk.data.path.insert(0, pathjoin(dirname(dirname(dirname(__file__))), 'nltk_data'))


def generate_link_format_regex():
    o = ObjectId()
    inner_regex = r'([a-f\d]{24})'
    bson_string = encode_bson_to_string(o)
    # TODO: Temporary fix.
    # Strip the whitespace in the encoding and allow one or more spaces.
    # Note: re.escape also escapes spaces, which is why the replace looks for '\\ '.
    pattern = re.escape(bson_string).replace(str(o), inner_regex).replace('\\ ', r'\s*')
    return re.compile(pattern)


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

    async def create_user(self, username, password, name, email):
        # TODO: Check the username is not currently in use.
        password_hash = super().hash_password(password)
        inserted_id = await self.client.create_user(
            username=username,
            password_hash=password_hash,
            name=name,
            email=email,
            bio=None,
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

    async def get_user_stories(self, user_id):
        stories = await self.client.get_user_stories(user_id)
        story_id_map = {}
        for story in stories:
            story_id = story['story_id']
            last_pos = story['position_context']
            story_id_map[story_id] = last_pos
        story_summaries = await self._get_stories_or_wikis_by_ids(user_id, story_id_map.keys(), 'story')
        for story_summary in story_summaries:
            story_summary['position_context'] = story_id_map[story_summary['story_id']]
        return story_summaries

    async def get_user_wikis(self, user_id):
        wiki_ids = await self.client.get_user_wiki_ids(user_id)
        wikis = await self._get_stories_or_wikis_by_ids(user_id, wiki_ids, 'wiki')
        return wikis

    @staticmethod
    def _get_current_user_access_level_in_object(user_id, obj):
        for user in obj['users']:
            if user['user_id'] == user_id:
                return user['access_level']

    async def _get_stories_or_wikis_by_ids(self, user_id, object_ids, object_type):
        objects = []
        for object_id in object_ids:
            if object_type == 'story':
                obj = await self.client.get_story(object_id)
            elif object_type == 'wiki':
                obj = await self.client.get_wiki(object_id)
            else:
                raise ValueError("invalid object type: {}".format(object_type))
            access_level = self._get_current_user_access_level_in_object(user_id, obj)
            id_key = '{}_id'.format(object_type)
            objects.append({
                id_key:         obj['_id'],
                'title':        obj['title'],
                'access_level': access_level,
            })
        return objects

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
            # TODO: Handle case when client provides bad paragraph_id
            raise
        else:
            paragraph_id = ObjectId()
            await self.client.insert_paragraph(paragraph_id, '', to_section_id=section_id, at_index=index)
            await self.client.insert_links_for_paragraph(paragraph_id, list(), in_section_id=section_id, at_index=index)
            await self.client.insert_note_for_paragraph(paragraph_id, '', in_section_id=section_id, at_index=index)
            if text is not None:
                await self.set_paragraph_text(section_id, text, paragraph_id)
            return paragraph_id

    async def get_story(self, story_id):
        story = await self.client.get_story(story_id)
        return story

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
        notes = section['notes']
        paragraphs = section['content']
        for index in range(len(paragraphs)):
            note = notes[index]['note']
            if note != '':
                paragraphs[index]['note'] = note
        return paragraphs

    async def set_story_title(self, story_id, title):
        story = await self.client.get_story(story_id)
        try:
            await self.client.set_story_title(story_id, title)
            await self.client.set_section_title(story['section_id'], title)
        except ClientError:
            # TODO: Deal with this
            raise
        else:
            # TODO: Should this return something?
            pass

    async def set_section_title(self, section_id, title):
        await self.client.set_section_title(section_id, title)

    async def set_paragraph_text(self, section_id, text, paragraph_id):
        sentences_and_links = await self.get_links_from_paragraph(text)
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

    @staticmethod
    def _update_link_in_references_with_context(references, link_id, context):
        for reference in references:
            if reference['link_id'] == link_id:
                reference['context'] = context
                break

    async def get_links_from_paragraph(self, paragraph_text):
        # TODO: Support languages other than English.
        sentences = nltk.sent_tokenize(paragraph_text)
        results = []
        for sentence in sentences:
            sentence_links = []
            potential_link_ids = map(ObjectId, re.findall(self.link_format_regex, sentence))
            for potential_id in potential_link_ids:
                link = await self.get_link(potential_id)
                if link is not None:
                    sentence_links.append(link)
            if sentence_links:
                sentence_tuple = (sentence, sentence_links)
                results.append(sentence_tuple)
        return results

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

    async def delete_paragraph(self, section_id, paragraph_id):
        link_ids = await self.client.get_links_in_paragraph(paragraph_id, section_id)
        for link_id in link_ids:
            await self.delete_link(link_id)
        await self.client.delete_paragraph(section_id, paragraph_id)

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
        alias_id = await self._create_alias(page_id, title)
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
            # TODO: Deal with this.
            raise
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
            # TODO: Deal with this.
            raise
        else:
            # TODO: Should this return something?
            pass

    async def get_wiki(self, wiki_id):
        wiki = await self.client.get_wiki(wiki_id)
        return wiki

    async def get_wiki_hierarchy(self, wiki_id):
        # TODO: Build wiki link table
        wiki = await self.get_wiki(wiki_id)
        segment_id = wiki['segment_id']
        return await self.get_segment_hierarchy(segment_id)

    async def get_segment_hierarchy(self, segment_id):
        # TODO: Build wiki link table
        segment = await self.client.get_segment(segment_id)
        hierarchy = {
            'title':      segment['title'],
            'segment_id': segment_id,
            'segments':   [],  #[await self.get_segment_hierarchy(seg_id) for seg_id in segment['segments']],
            'pages':      [],  #[await self.get_page_for_hierarchy(page_id) for page_id in segment['pages']],
            # 'links':      {},
            'links':      [],
        }
        segments = hierarchy['segments']
        links = hierarchy['links']
        pages = hierarchy['pages']
        # Iterate through the segments, popping out the `links` field and inserting them into the top-level `links`.
        for segment_id in segment['segments']:
            inner_segment = await self.get_segment_hierarchy(segment_id)
            links.extend(inner_segment.pop('links'))
            segments.append(inner_segment)
        # Iterate through the pages, pulling the links from the aliases inside of each.
        for page_id in segment['pages']:
            page = await self.get_page_for_hierarchy(page_id)
            aliases = page.pop('aliases')
            pages.append(page)
            for name, alias_id in aliases.items():
                alias = await self.client.get_alias(alias_id)
                for link_id in alias['links']:
                    link = {
                        'link_id': link_id,
                        'name':    name,
                        'page_id': page_id
                    }
                    links.append(link)
                    # links[link_id] = {'name': name, 'page_id': page_id}
        return hierarchy

    async def get_page_for_hierarchy(self, page_id):
        page = await self.client.get_page(page_id)
        return {
            'title':   page['title'],
            'page_id': page_id,
            'aliases': page['aliases'],
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
            # TODO: Deal with this
            raise
        else:
            # TODO: Should this return something?
            pass

    async def set_segment_title(self, title, segment_id):
        try:
            await self.client.set_segment_title(title, segment_id)
        except ClientError:
            # TODO: Deal with this
            raise
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
            # TODO: Deal with this
            raise
        else:
            # TODO: Should this return something?
            pass

    async def set_heading_text(self, title, text, page_id):
        try:
            await self.client.set_heading_text(title, text, page_id)
        except ClientError:
            # TODO: Deal with this
            raise
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
        await self.delete_segment(segment_id)
        # Delete the wiki proper.
        await self.client.delete_wiki(wiki_id)

    async def delete_segment(self, segment_id):
        await self.recur_delete_segment_and_subsegments(segment_id)

    async def recur_delete_segment_and_subsegments(self, segment_id):
        segment = await self.client.get_segment(segment_id)
        for subsegment_id in segment['segments']:
            await self.recur_delete_segment_and_subsegments(subsegment_id)
        for page_id in segment['pages']:
            await self.delete_page(page_id)
        await self.client.delete_segment(segment_id)

    async def delete_template_heading(self, title, segment_id):
        try:
            await self.client.delete_template_heading(title, segment_id)
        except ClientError:
            raise
        else:
            pass

    async def delete_page(self, page_id):
        page = await self.client.get_page(page_id)
        for alias_id in page['aliases'].values():
            await self._delete_alias_no_replace(alias_id)
        await self.client.delete_page(page_id)

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
        await self._delete_alias_no_replace(alias_id)
        alias_name = alias['name']
        page_id = alias['page_id']
        page = await self.client.get_page(page_id)
        # Alias with page title deleted, need to recreate primary alias
        if page is not None and not await self._page_title_is_alias(page):
            await self._create_alias(page_id, alias_name)

    async def _delete_alias_no_replace(self, alias_id: ObjectId):
        alias = await self.get_alias(alias_id)
        alias_name = alias['name']
        for link_id in alias['links']:
            await self.comprehensive_remove_link(link_id, alias_name)
        page_id = alias['page_id']
        await self.client.remove_alias_from_page(alias_name, page_id)
        await self.client.delete_alias(alias_id)

    async def _create_alias(self, page_id: ObjectId, name: str):
        alias_id = await self.client.create_alias(name, page_id)
        await self.client.insert_alias_to_page(page_id, name, alias_id)
        return alias_id

    async def _page_title_is_alias(self, page):
        title = page['title']
        return page['aliases'].get(title) is not None


class MongoDBTornadoInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorTornadoClient, db_name, db_host, db_port, db_user, db_pass)


class MongoDBAsyncioInterface(MongoDBInterface):
    def __init__(self, db_name, db_host, db_port, db_user=None, db_pass=None):
        super().__init__(MongoDBMotorAsyncioClient, db_name, db_host, db_port, db_user, db_pass)
