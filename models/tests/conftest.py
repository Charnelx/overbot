# pylint: disable=unused-argument
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments

from unittest import mock
from pathlib import Path
import pkgutil
from random import randint
import sys

from mongoengine import connect, disconnect
from mongomock.helpers import utcnow
import pytest

from scrapper.models.overclockers_models import Author, Topic


@pytest.fixture(scope='function')
def mock_adapter_db_settings(monkeypatch):
    settings_mock = mock.Mock()
    settings_mock.SCRAPPER_DATABASES = {
        'default': {
            'db': 'mongoenginetest',
            'host': 'mongomock://localhost',
            'port': None
        }
    }

    monkeypatch.setattr(sys.modules['scrapper.models.adapters'], 'settings', settings_mock)


@pytest.fixture(scope='function')
def mock_db_connection_on_module_level(monkeypatch):
    level_up_path = Path(globals().get('__package__')).stem
    modules = [name for _, name, _ in pkgutil.iter_modules([str(Path(__file__).parent.absolute().parent.absolute())])]
    modules_path = []
    for module in modules:
        modules_path.append(f'{level_up_path}.{module}')

    for path in modules_path:
        try:
            monkeypatch.setattr(sys.modules[path], 'connect', lambda *args, **kwargs: True)
        except AttributeError:
            pass


@pytest.fixture(scope='function')
def mocked_db_connection():
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
