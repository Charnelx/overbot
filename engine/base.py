from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Optional, Union

from fake_useragent import FakeUserAgent

from scrapper.utils.spelling.checker import validate_location


class BaseScraper(ABC):

    @property
    @abstractmethod
    def HOST(self) -> str:  # noqa: N802
        pass

    @property
    @abstractmethod
    def DOMAIN(self) -> str:  # noqa: N802
        pass


class ScrapperMixin(BaseScraper):

    HOST = ''
    DOMAIN = ''

    def __init__(self, *args, **kwargs):
        self._ua = FakeUserAgent()

    @property
    def _headers_partial(self) -> dict:
        return {
            'Host': self.HOST,
            'Referer': self.DOMAIN
        }

    def generate_headers(self) -> dict:
        headers = self._headers_partial
        headers.update(
            {'User-Agent': self._ua.random}
        )
        return headers


class DataContainerMixin:

    TOPIC_ID_PATTERN = re.compile(r'\D+', re.IGNORECASE)
    COUNTRY_PATTERN = re.compile(r'(ук.*на)', re.IGNORECASE)

    def parse_topic_id(self, path: str) -> int:
        return int(re.sub(self.TOPIC_ID_PATTERN, '', path.rsplit('&', 1)[1]))


@dataclass
class TopicMetaInfo(DataContainerMixin):

    domain: str
    url: str
    title: str
    author: str
    author_profile_link: str
    posts_count: Union[str, int]
    views_count: Union[str, int]
    last_post_timestamp: Union[str, datetime]
    location_raw: Optional[str] = None
    location: Optional[str] = None
    page_index: Optional[int] = None
    topic_id: Optional[int] = None
    topic_content: Optional[str] = None
    processed: bool = False

    def process(self) -> None:
        relative_path = self.url.split('.', 1)[1].rsplit('&', 1)[0]
        self.url = f'{self.domain}{relative_path}'
        self.posts_count = int(self.posts_count.strip())
        self.views_count = int(self.views_count.strip())
        self.last_post_timestamp = datetime.strptime(self.last_post_timestamp, '%Y-%m-%dT%H:%M:%S%z')
        self.topic_id = self.parse_topic_id(path=relative_path)
        self.author_profile_link = self.author_profile_link.split('.', 1)[1].rsplit('&', 1)[0]
        self.author_profile_link = f'{self.domain}{self.author_profile_link}'

        location_pair = self.title.split(']')[0].strip('[').split(',')
        self.location_raw = ','.join(location_pair)
        location_length = len(location_pair)

        # replace country name with regex
        if location_length == 1 and not re.match(self.COUNTRY_PATTERN, location_pair[0]):
            self.location = validate_location(location_pair[0].strip())
        elif location_length == 2:
            if re.match(self.COUNTRY_PATTERN, location_pair[0]):
                # example: Украина, Киев
                location_name = location_pair[1].strip()
            else:
                # example: Покровск,Донецкая область
                location_name = ','.join(location_pair).strip()

            if ',' in location_name:
                # example: Верховцево, Днепропетровская область
                location_name = location_name.split(',')[0]
            elif '/' in location_name:
                location_name = location_name.split('/')[0]
            elif ' и ' in location_name:
                # example: Киев и Одесса
                location_name = location_name.split(' ')[0]
            elif '-' in location_name:
                # example: Ивано - Франковск
                location_name = location_name.replace(' ', '')
            self.location = validate_location(location_name)
        else:
            self.location = None

        self.title = self.title.split(']')[1].strip()

        self.processed = True

    def to_json(self):
        if self.processed:
            return {
                'topic_id': self.topic_id,
                'url': self.url,
                'title': self.title,
                'posts_count': self.posts_count,
                'views_count': self.views_count,
                'last_post_timestamp': self.last_post_timestamp,
                'location_raw': self.location_raw,
                'location': self.location,
                'topic_content': self.topic_content
            }
        raise AttributeError('Values was not processed. Call process method.')


@dataclass
class TopicData(DataContainerMixin):

    content: str
    url: str
    topic_id: Optional[int] = None

    def process(self) -> None:
        self.topic_id = self.parse_topic_id(path=self.url)
