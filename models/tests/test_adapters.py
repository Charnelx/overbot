# pylint: disable=no-self-use
# pylint: disable=no-member
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods

from random import randint

import pytest

from ..adapters import TopicsToDBAdapter
from ..overclockers_models import Author, Topic

# pylint: disable=unused-argument
@pytest.mark.usefixtures("mocked_db_connection")
@pytest.mark.usefixtures("mock_db_connection_on_module_level")
class TestTopicsToDBAdapter:

    def test_connect(self, mock_adapter_db_settings):
        adapter = TopicsToDBAdapter()
        adapter.connect()

        assert adapter.connection is True

    def test_import_topics_to_db(self, mock_adapter_db_settings, create_topic_meta_info):
        adapter = TopicsToDBAdapter()
        adapter.connect()

        topics = []
        for _ in range(10):
            topic = create_topic_meta_info()
            topic.process()
            topic.topic_id = randint(1000, 1000000)
            topics.append(topic)

        result = adapter.import_topics_to_db(topics)

        assert result.upserted_count == 10

        topics = Topic.objects.all()

        assert Author.objects.count() == 1
        assert len(topics) == 10
        assert Topic.objects.first().topic_id == topics[0].topic_id

    def test_import_topics_to_db_without_process_called(self, mock_adapter_db_settings, create_topic_meta_info):
        adapter = TopicsToDBAdapter()
        adapter.connect()

        topic = create_topic_meta_info()
        topic.author_profile_link = 'https://forum.example.com/memberlist.php?mode=viewprofile&u=123456'

        with pytest.raises(AttributeError) as err:
            _ = adapter.import_topics_to_db([topic])

        assert str(err.value) == 'Values was not processed. Call process method first.'
        assert Author.objects.count() == 1
        assert Topic.objects.count() == 0
