# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods

from unittest import mock

import pytest

from ..helpers import fake_semaphore


class TestUtils:

    @pytest.mark.asyncio
    async def test_fake_semaphore(self):
        with mock.patch('scrapper.utils.helpers.asyncio.sleep') as sleep_mock:
            async with fake_semaphore() as semaphore:
                pass

        assert semaphore is None
        assert sleep_mock.await_count == 1
