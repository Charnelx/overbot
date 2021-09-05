from typing import Optional

import pytest

from scrapper.engine.base import TopicData


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
