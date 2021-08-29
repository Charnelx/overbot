from datetime import datetime, timezone
from typing import Optional

import pytest

from scrapper.engine.base import TopicMetaInfo, TopicData


@pytest.fixture
def create_topic_meta_info():
    def inner(url: Optional[str] = None, title: Optional[str] = None, location_raw: Optional[str] = None):
        return TopicMetaInfo(
            domain='forum.example.com',
            url=url if url else './viewtopic.php?f=26&t=1000&sid=abc123',
            title=title if title else '[Украина, Киев] Title',
            author='Nickname',
            author_profile_link='https://example.com/nickname',
            posts_count='100',
            views_count='100',
            last_post_timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            location_raw=location_raw if location_raw else 'Украина, Киев'
        )
    return inner


@pytest.fixture
def create_topic_data():
    def inner(url: Optional[str] = None, content='', topic_id: Optional[int] = None, closed: bool = False):
        return TopicData(
            content=content,
            url=url if url else './viewtopic.php?f=26&t=1000&sid=abc123',
            topic_id=topic_id if topic_id else None,
            closed=closed
        )
    return inner
