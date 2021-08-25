import asyncio
import aiohttp
from aiohttp.typedefs import Any, StrOrURL
import logging

from scrapper.utils.exceptions import RetriesExceeded
from scrapper.utils.helpers import fake_semaphore


logger = logging.getLogger(__name__)


class GSession(aiohttp.ClientSession):

    async def get(
            self, url: StrOrURL, *, allow_redirects=True, semaphore=None, retry_num=3, sleep_on_retry=None, **kwargs
    ):
        retries = 0

        semaphore = semaphore if semaphore else fake_semaphore()
        retry_num = kwargs.pop('retry_num', 3)

        while True:
            async with semaphore:
                try:
                    async with super().get(url, allow_redirects=allow_redirects, **kwargs) as response:
                        if response.content_type == 'application/json':
                            content = await response.json()
                        else:
                            content = await response.text()
                        response._content = content if content else None

                        return response
                except asyncio.TimeoutError:
                    retries += 1
                    if retries == retry_num:
                        logger.exception('Request aborted due to retries limit exceeded')
                        raise RetriesExceeded(
                            f'Retry limit exceeded ({retries} of {retry_num}) for GET {url} '
                        )
                    elif sleep_on_retry:
                        logger.info(
                            f'GET request waiting {sleep_on_retry} sec for {url} to retry ({retries} of {retry_num})'
                        )
                        await asyncio.sleep(sleep_on_retry)
                    else:
                        logger.exception(f'GET {url} request failed on timeout')
                except Exception:
                    logger.exception(f'Exception raised during processing of GET {url} request')
                    raise

    async def post(self, url: StrOrURL, *, data: Any = None, **kwargs: Any):
        semaphore = kwargs.pop('semaphore', None)
        retry_num = kwargs.pop('retry_num', 3)
        sleep_on_retry = kwargs.pop('sleep_on_retry', False)

        retries = 0
        semaphore = semaphore if semaphore else fake_semaphore()
        while True:
            async with semaphore:
                try:
                    async with super().post(url, data=data, **kwargs) as response:
                        if response.content_type == 'application/json':
                            content = await response.json()
                        else:
                            content = await response.text()
                        response._content = content if content else None

                        return response
                except asyncio.TimeoutError:
                    retries += 1
                    if retries == retry_num:
                        logger.exception('Request aborted due to retries limit exceeded')
                        raise RetriesExceeded(
                            f'Retry limit exceeded ({retries} of {retry_num}) for POST {url} '
                        )
                    elif sleep_on_retry:
                        logger.info(
                            f'POST request waiting {sleep_on_retry} sec for {url} to retry ({retries} of {retry_num})'
                        )
                        await asyncio.sleep(sleep_on_retry)
                    else:
                        logger.exception(f'POST {url} request failed on timeout')
                except Exception:
                    logger.exception(f'Exception raised during processing of POST {url} request')
                    raise