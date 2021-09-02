# pylint: disable=no-self-use

import logging
from unittest import mock

import pytest

from ..session import GSession
from ..exceptions import RetriesExceeded


LOGGER = logging.getLogger(__name__)
LOGGER.propagate = True


class TestGSession:

    @pytest.mark.asyncio
    async def test_get_data_text_response(self, create_async_request_context_manager):
        expected_response = 'some_response'

        session = GSession()

        waiting = create_async_request_context_manager(result=expected_response)

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            req.return_value = waiting

            result = await session.get_data('https://example.com')

            assert req.called is True
            assert result.data == expected_response

    @pytest.mark.asyncio
    async def test_get_data_json_response(self, create_async_request_context_manager):
        expected_response = {'result': 'some_result'}

        session = GSession()

        waiting = create_async_request_context_manager(content_type='application/json', result=expected_response)

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            req.return_value = waiting

            result = await session.get_data('https://example.com')

            assert req.called is True
            assert result.data == expected_response

    @pytest.mark.asyncio
    async def test_get_data_retries_exceeded(self, create_async_request_context_manager):
        url = 'https://example.com'

        session = GSession()

        waiting = create_async_request_context_manager(
            content_type='application/json',
            result=dict(),
            raise_error=True
        )

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            with pytest.raises(RetriesExceeded) as err:
                req.return_value = waiting

                _ = await session.get_data('https://example.com', retry_num=1)

                assert req.called is True
                assert str(err.value) == f'Retry limit exceeded (1 of 1) for GET {url}'

        await session.close()

    @pytest.mark.asyncio
    async def test_get_data_sleep_on_retry(self, create_async_request_context_manager, caplog):
        caplog.set_level(logging.INFO)

        url = 'https://example.com'
        sleep_before_retry = 1  # do not set high values since this is an actual time (sec) method will be "sleeping"

        session = GSession()

        waiting = create_async_request_context_manager(
            content_type='application/json',
            result=dict(),
            raise_error=True
        )

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            with pytest.raises(RetriesExceeded) as err:
                req.side_effect = [waiting, waiting]

                _ = await session.get_data('https://example.com', retry_num=2, sleep_on_retry=sleep_before_retry)

        assert req.called is True
        assert str(err.value) == f'Retry limit exceeded (2 of 2) for GET {url}'
        assert caplog.messages[0] == f'GET request waiting {sleep_before_retry} sec for {url} to retry (1 of 2)'
        assert caplog.messages[1] == 'Request aborted due to retries limit exceeded'

        await session.close()

    @pytest.mark.asyncio
    async def test_get_data_no_sleep_on_retry(self, create_async_request_context_manager, caplog):
        caplog.set_level(logging.INFO)

        url = 'https://example.com'
        sleep_before_retry = False

        session = GSession()

        waiting = create_async_request_context_manager(
            content_type='application/json',
            result=dict(),
            raise_error=True
        )

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            with pytest.raises(RetriesExceeded) as err:
                req.side_effect = [waiting, waiting]

                _ = await session.get_data('https://example.com', retry_num=2, sleep_on_retry=sleep_before_retry)

        assert req.called is True
        assert str(err.value) == f'Retry limit exceeded (2 of 2) for GET {url}'
        assert caplog.messages[0] == f'GET {url} request failed on timeout'

        await session.close()

    @pytest.mark.asyncio
    async def test_get_data_general_exception(self, create_async_request_context_manager, caplog):
        caplog.set_level(logging.INFO)

        url = 'https://example.com'
        sleep_before_retry = False

        session = GSession()

        waiting = create_async_request_context_manager(
            content_type='application/json',
            result=dict(),
            raise_error=True,
            exception=Exception
        )

        with mock.patch('scrapper.utils.session.aiohttp.ClientSession.get') as req:
            with pytest.raises(Exception):
                req.side_effect = [waiting, waiting]

                _ = await session.get_data('https://example.com', retry_num=2, sleep_on_retry=sleep_before_retry)

        assert req.called is True
        assert caplog.messages[0] == f'Exception raised during processing of GET {url} request'

        await session.close()
