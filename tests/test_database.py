from loom import database

import asyncio
import pytest


class TestDatabase:
    def setup(self):
        self.client = database.LoomMongoDBMotorAsyncioClient('test')

    def teardown(self):
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(self.client.drop_database())
        event_loop.close()

    @pytest.mark.asyncio
    async def test_get_user_preferences(self):
        pass

    @pytest.mark.asyncio
    async def test_get_user_story_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_user_wiki_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_user_story_and_wiki_ids(self):
        pass

    @pytest.mark.asyncio
    async def test_get_story(self):
        pass

    @pytest.mark.asyncio
    async def test_get_section(self):
        pass

    @pytest.mark.asyncio
    async def test_get_wiki(self):
        pass

    @pytest.mark.asyncio
    async def test_get_segment(self):
        pass

    @pytest.mark.asyncio
    async def test_get_page(self):
        pass

    @pytest.mark.asyncio
    async def test_get_heading(self):
        pass

    @pytest.mark.asyncio
    async def test_get_content(self):
        pass

    @pytest.mark.asyncio
    async def test_get_paragraph(self):
        pass

    @pytest.mark.asyncio
    async def test_create_user(self):
        pass

    @pytest.mark.asyncio
    async def test_create_story(self):
        pass

    @pytest.mark.asyncio
    async def test_create_section(self):
        pass

    @pytest.mark.asyncio
    async def test_create_wiki(self):
        pass

    @pytest.mark.asyncio
    async def test_create_segment(self):
        pass

    @pytest.mark.asyncio
    async def test_create_page(self):
        pass

    @pytest.mark.asyncio
    async def test_create_heading(self):
        pass

    @pytest.mark.asyncio
    async def test_create_content(self):
        pass

    @pytest.mark.asyncio
    async def test_create_paragraph(self):
        pass
