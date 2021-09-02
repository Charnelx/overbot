import asyncio
import logging

import aiohttp
from aiohttp.typedefs import StrOrURL

from scrapper.utils.exceptions import RetriesExceeded
from scrapper.utils.helpers import fake_semaphore


logger = logging.getLogger(__name__)


class GSession(aiohttp.ClientSession):

    async def get_data(
            self, url: StrOrURL, *, allow_redirects=True, semaphore=None, retry_num=3, sleep_on_retry=None, **kwargs
    ):
        retries = 0

        while True:
            async with semaphore if semaphore else fake_semaphore():
                try:
                    async with super().get(url, allow_redirects=allow_redirects, **kwargs) as response:
                        if response.content_type == 'application/json':
                            content = await response.json()
                        else:
                            content = await response.text()
                        response.data = content if content else None

                        return response
                except asyncio.TimeoutError as err:
                    retries += 1
                    if retries == retry_num:
                        logger.exception('Request aborted due to retries limit exceeded')
                        raise RetriesExceeded(
                            f'Retry limit exceeded ({retries} of {retry_num}) for GET {url}'
                        ) from err
                    if sleep_on_retry:
                        logger.info(
                            'GET request waiting %i sec for %s to retry (%i of %i)',
                            sleep_on_retry, url, retries, retry_num
                        )
                        await asyncio.sleep(sleep_on_retry)
                    else:
                        logger.exception('GET %s request failed on timeout', url)
                except Exception:
                    logger.exception('Exception raised during processing of GET %s request', url)
                    raise
