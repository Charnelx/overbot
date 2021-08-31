# pylint: disable=no-self-use
# pylint: disable=protected-access

from asyncio import ProactorEventLoop
from unittest import mock
import logging

import pytest

from scrapper.engine.over_scrapper import OverclockersScrapper

LOGGER = logging.getLogger(__name__)
LOGGER.propagate = True


class TestOverclockersScrapper:

    def test_set_event_loop(self):
        scrapper = OverclockersScrapper()
        scrapper._set_event_loop()

        assert scrapper._event_loop_set is True
        assert isinstance(scrapper.loop, ProactorEventLoop)

    @pytest.mark.parametrize('page_number', list(range(1, 10)))
    def test__generate_page_id(self, page_number):
        scrapper = OverclockersScrapper()
        pages = list(scrapper._generate_page_id(1, page_number))

        assert len(pages) == page_number
        assert all(filter(lambda idx: idx % 40, pages)) is True

    @pytest.mark.parametrize('page_number', list(range(1, 10)))
    def test__generate_listing_urls(self, page_number):
        scrapper = OverclockersScrapper()
        url_pairs = scrapper._generate_listing_urls(1, page_number)

        assert url_pairs[0][0] == scrapper.FORUM_URL
        assert url_pairs[0][1] == {'f': scrapper.FORUM_ID, 'start': 0}
        assert len(url_pairs) == page_number

    @pytest.mark.asyncio
    async def test_fire_requests(self):
        expected_result = 'some_result'

        scrapper = OverclockersScrapper()
        urls = scrapper._generate_listing_urls(1, 1)

        with mock.patch('scrapper.engine.over_scrapper.OverclockersScrapper._get_data') as req:
            req.return_value = expected_result
            result = await scrapper._fire_requests(urls)

        assert req.called is True
        assert len(result) == 1
        assert result[0] == expected_result

    @pytest.mark.parametrize('page_number', list(range(1, 10)))
    def test_get_topics(self, page_number):
        scrapper = OverclockersScrapper()

        with mock.patch('scrapper.engine.over_scrapper.OverclockersScrapper._fire_requests') as req_result:
            with mock.patch('scrapper.engine.over_scrapper.OverclockersParser.parse_topics_list') as parser_result:
                req_result.return_value = [{'https://example.com/topics-list': ''} for _ in range(page_number)]
                parser_result.return_value = [mock.Mock()]
                result = scrapper.get_topics(1, page_number)

        assert req_result.called is True
        assert parser_result.called is True
        assert len(result) == page_number
        assert result[-1].page_index == page_number - 1

    @pytest.mark.parametrize('page_number', list(range(1, 10)))
    def test_get_topics_on_exception(self, page_number, caplog):
        caplog.set_level(logging.ERROR)

        scrapper = OverclockersScrapper()

        with mock.patch('scrapper.engine.over_scrapper.OverclockersScrapper._fire_requests') as req_result:
            with mock.patch('scrapper.engine.over_scrapper.OverclockersParser.parse_topics_list') as parser_result:
                req_result.return_value = [Exception('Something happened')]
                parser_result.return_value = [mock.Mock()]
                result = scrapper.get_topics(1, page_number)

        assert req_result.called is True
        assert parser_result.called is False
        assert caplog.messages[0] == 'Something happened'
        assert len(result) == 0

    @pytest.mark.parametrize('page_number', list(range(1, 10)))
    def test_get_topics_content(self, page_number):
        scrapper = OverclockersScrapper()

        with mock.patch('scrapper.engine.over_scrapper.OverclockersScrapper._fire_requests') as req_result:
            with mock.patch('scrapper.engine.over_scrapper.OverclockersParser.parse_topic_content') as parser_result:
                req_result.return_value = [{'https://example.com/topics-list': ''} for _ in range(page_number)]
                parser_result.return_value = [mock.Mock()]
                result = scrapper.get_topics_content('https://example.com/topic')

        assert req_result.called is True
        assert parser_result.called is True
        assert len(result) == page_number

    def test_get_topics_content_on_exception(self, caplog):
        caplog.set_level(logging.ERROR)

        scrapper = OverclockersScrapper()

        with mock.patch('scrapper.engine.over_scrapper.OverclockersScrapper._fire_requests') as req_result:
            with mock.patch('scrapper.engine.over_scrapper.OverclockersParser.parse_topic_content') as parser_result:
                req_result.return_value = [Exception('Something happened')]
                parser_result.return_value = [mock.Mock()]
                result = scrapper.get_topics_content('https://example.com/topic')

        assert req_result.called is True
        assert parser_result.called is False
        assert caplog.messages[0] == 'Something happened'
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_data(self):

        # pylint: disable=unused-argument
        # pylint: disable=too-few-public-methods
        async def fake_get_data(*args, **kwargs):
            class FakeResponse:
                data = 'some_data'
                url = 'https://example.com/topic'
            return FakeResponse()

        scrapper = OverclockersScrapper()
        url = scrapper._generate_listing_urls(1, 1)[0]

        mocked_session = mock.AsyncMock()
        mocked_session.get_data = fake_get_data

        result = await scrapper._get_data(url, None, mocked_session, None)

        assert result == {'https://example.com/topic': 'some_data'}
