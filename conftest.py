from datetime import datetime, timezone
from typing import Optional

import pytest

from scrapper.engine.base import TopicMetaInfo


@pytest.fixture
def create_topic_meta_info():
    def inner(url: Optional[str] = None, title: Optional[str] = None, location_raw: Optional[str] = None):
        return TopicMetaInfo(
            domain='https://forum.example.com',
            url=url if url else './viewtopic.php?f=26&t=1000&sid=abc123',
            title=title if title else '[Украина, Киев] Title',
            author='Nickname',
            author_profile_link='./memberlist.php?mode=viewprofile&u=123456',
            posts_count='100',
            views_count='100',
            last_post_timestamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            location_raw=location_raw if location_raw else 'Украина, Киев'
        )
    return inner
