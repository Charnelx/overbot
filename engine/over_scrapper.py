import asyncio
import logging
from typing import Generator, List

from scrapper.engine.base import ScrapperMixin
from scrapper.utils.session import GSession

from .over_parser import OverclockersParser
from .types import URLContent


class OverclockersScrapper(ScrapperMixin):

    HOST = 'forum.overclockers.ua'
    DOMAIN = f'https://{HOST}'
    FORUM_URL = f'{DOMAIN}/viewforum.php'
    TOPIC_URL = f'{DOMAIN}/viewtopic.php'
    FORUM_ID = 26

    def __init__(self, coros_limit=100, r_timeout=5, pause=15, raise_exceptions=True):
        super().__init__()
        self.loop = None
        self.r_timeout = r_timeout
        self.coros_limit = coros_limit
        self.raise_exceptions = raise_exceptions
        self.pause = pause
        self._event_loop_set = False

    def _set_event_loop(self):
        if not self._event_loop_set:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self._event_loop_set = True

    @staticmethod
    def _generate_page_id(start: int, end: int) -> Generator[int, int, None]:
        for i in range(start - 1, end):
            yield i * 40

    def _generate_listing_urls(self, start: int, end: int) -> List[tuple]:
        urls = []
        for page_index in self._generate_page_id(start, end):
            req_params = {'f': self.FORUM_ID, 'start': page_index}
            urls.append(
                (
                    self.FORUM_URL,
                    req_params
                )
            )
        return urls

    async def _fire_requests(self, urls):
        session = GSession(headers=self.generate_headers())
        semaphore = asyncio.Semaphore(self.coros_limit)

        tasks, result = [], []

        for url, req_params in urls:
            tasks.append(self._get_data(url, req_params, session, semaphore))

        result = await asyncio.gather(*tasks, return_exceptions=self.raise_exceptions)

        await session.close()
        return result

    async def _get_data(self, url, req_params, session, semaphore) -> URLContent:
        data = None
        response = await session.get_data(
            url,
            params=req_params,
            semaphore=semaphore,
            timeout=self.r_timeout,
            sleep_on_retry=self.pause
        )
        if response and response.data:
            data = {str(response.url): response.data}
        return data

    def get_topics(self, page_num_start: int, page_num_end: int):

        self._set_event_loop()

        topics_listing = []
        parser = OverclockersParser(domain=self.DOMAIN)

        urls = self._generate_listing_urls(page_num_start, page_num_end)
        results_raw = self.loop.run_until_complete(self._fire_requests(urls))

        for page_index, page in enumerate(results_raw):
            if isinstance(page, Exception):
                logging.error(page)
            else:
                for data_raw in page.values():
                    data = parser.parse_topics_list(data_raw)
                    for item in data:
                        item.page_index = page_index
                        topics_listing.append(item)
        return topics_listing

    def get_topics_content(self, urls):
        self._set_event_loop()

        topics_listing = []
        parser = OverclockersParser(domain=self.DOMAIN)

        results_raw = self.loop.run_until_complete(self._fire_requests(urls))

        for page in results_raw:
            if isinstance(page, Exception):
                logging.error(page)
            else:
                for url, data_raw in page.items():
                    data = parser.parse_topic_content(data_raw, url)
                    topics_listing.append(data)
        return topics_listing
