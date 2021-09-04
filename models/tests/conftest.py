# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

from random import randint

from mongoengine import connect, disconnect
from mongomock.helpers import utcnow
import pytest

from scrapper.models.overclockers_models import Author, Topic


@pytest.fixture
def mocked_db_connection(scope='function'):
    connect('mongoenginetest', host='mongomock://localhost')
    yield None
    disconnect()


@pytest.fixture
def create_author():
    def inner(nickname='joedoe', profile_link='https://example.com'):
        author = Author(nickname='joedoe', profile_link='https://example.com')
        author.save()
        return author
    return inner


@pytest.fixture
def create_topic(create_author):
    timestamp = utcnow()

    def inner(
            author=None, created=timestamp, updated=timestamp, topic_id=randint(1, 100000), url='https://example.com',
            title='Some topic title', posts_count=1, views_count=1, last_post_timestamp=timestamp,
            location_raw='Украина, Киев', location='киев', topic_content='some content'
    ):
        author = author if author else create_author()

        topic = Topic(
            created=created,
            updated=updated,
            topic_id=topic_id,
            url=url,
            title=title,
            author=author,
            posts_count=posts_count,
            views_count=views_count,
            last_post_timestamp=last_post_timestamp,
            location_raw=location_raw,
            location=location,
            topic_content=topic_content
        )

        topic.save()
        return topic
    return inner
