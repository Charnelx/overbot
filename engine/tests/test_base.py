# pylint: disable=no-self-use

from datetime import datetime

import pytest

from scrapper.engine.base import ScrapperMixin


class TestScrapperMixin:

    def test_headers_partial_call(self):
        mixin = ScrapperMixin()
        mixin.DOMAIN = 'some_domain'
        mixin.HOST = 'some_host'

        # pylint: disable=protected-access
        assert mixin._headers_partial == {'Host': 'some_host', 'Referer': 'some_domain'}

    def test_generate_headers(self):
        mixin = ScrapperMixin()
        mixin.DOMAIN = 'other_domain'
        mixin.HOST = 'other_host'

        headers = mixin.generate_headers()
        user_agent_header = headers.pop('User-Agent')

        assert user_agent_header is not None
        assert headers == {'Host': 'other_host', 'Referer': 'other_domain'}


class TestTopicMetaInfo:

    def test_process_ok(self, create_topic_meta_info):
        topic = create_topic_meta_info()
        topic.process()

        assert topic.topic_id == 1000
        assert topic.title == 'Title'
        assert topic.closed is False
        assert topic.processed is True
        assert topic.location == 'киев'
        assert isinstance(topic.views_count, int)
        assert isinstance(topic.posts_count, int)
        assert topic.topic_content is None

    def test_location_single_length(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Днипро] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'днипро'

    def test_location_no_city(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Украина] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location is None

    def test_location_city_and_district_comma_separated(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Покровск, Донецкая область] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'покровск'

    def test_location_district_and_city_comma_separated(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Верховцево, Днепропетровская область] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'верховцево'

    def test_location_cities_slash_separated(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Украина, Киев/Бровары] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'киев'

    def test_location_cities_using_and_separation(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Украина, Одесса и Стамбул] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'одесса'

    def test_location_city_name_with_hyphen(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Украина, Ивано-Франковск] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'ивано-франковск'

    def test_location_separated_by_multiple_commas(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Украина, рівне, львів] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'ровно'

    def test_no_country_and_city_with_hyphen(self, create_topic_meta_info):
        topic = create_topic_meta_info(title='[Івано - Франківськ] GeForce for mining!')
        topic.process()

        assert topic.processed is True
        assert topic.location == 'ивано-франковск'

    def test_to_json_without_process_first(self, create_topic_meta_info):
        topic = create_topic_meta_info()

        with pytest.raises(AttributeError) as err:
            topic.to_json()

        assert str(err.value) == 'Values was not processed. Call process method first.'

    def test_to_json(self, create_topic_meta_info):
        topic = create_topic_meta_info()
        topic.process()

        assert topic.processed is True

        data = topic.to_json()

        updated_field = data.pop('updated')

        assert updated_field <= datetime.now()
        assert data == {
            'closed': False,
            'last_post_timestamp': topic.last_post_timestamp,
            'location': 'киев',
            'location_raw': 'Украина, Киев',
            'posts_count': 100,
            'title': 'Title',
            'topic_content': None,
            'topic_id': 1000,
            'url': 'forum.example.com/viewtopic.php?f=26&t=1000',
            'views_count': 100
        }

    def test_to_json_on_closed_topic(self, create_topic_meta_info):
        topic = create_topic_meta_info()
        topic.closed = True
        topic.process()

        assert topic.processed is True

        data = topic.to_json()

        updated_field = data.pop('updated')

        assert updated_field <= datetime.now()
        assert data == {
            'last_post_timestamp': topic.last_post_timestamp,
            'posts_count': 100,
            'topic_id': 1000,
            'views_count': 100
        }


class TestTopicData:

    def test_process(self, create_topic_data):
        topic_data = create_topic_data(url='./viewtopic.php?f=26&t=1000')
        topic_data.process()

        assert topic_data.topic_id == 1000

    def test_no_process_called(self, create_topic_data):
        topic_data = create_topic_data(url='./viewtopic.php?f=26&t=1000')

        assert topic_data.topic_id is None
