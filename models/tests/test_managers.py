from datetime import datetime, timedelta

from mongoengine.errors import ValidationError
from mongomock.helpers import utcnow
import pytest

from scrapper.models.overclockers_models import Author, Topic


@pytest.mark.usefixtures("mocked_db_connection")
class TestAuthorManager:

    def test_create_or_update(self):
        author = Author.objects.create_or_update(
            nickname='joedoe', profile_link='https://example.com'
        )

        assert Author.objects.count() == 1

        entry_from_db = Author.objects.first()

        assert entry_from_db._meta['collection'] == 'Authors'

        assert entry_from_db.nickname == author.nickname
        assert entry_from_db.profile_link == author.profile_link

    def test_author_creation_with_broken_link(self):
        with pytest.raises(ValidationError) as err:
            Author.objects.create_or_update(
                nickname='joedoe', profile_link='example.com'
            )

        assert str(err.value) == "Invalid scheme example.com in URL: example.com"
        assert Author.objects.count() == 0

    def test_get_existing_author(self, create_author):
        author = create_author()

        assert Author.objects.create_or_update(
            nickname=author.nickname, profile_link=author.profile_link
        ).id == author.id


@pytest.mark.usefixtures("mocked_db_connection")
class TestTopicManager:

    def test_fetch_excluded_topics(self, create_topic):
        past_timestamp = utcnow() - timedelta(minutes=15)

        topic = create_topic(updated=past_timestamp)

        assert Topic.objects.fetch_excluded_topics().count() == 0, 'Topic was updated 15 min ago so ' \
                                                                   '(out of context) it should not be excluded'

        topic.updated = utcnow()
        topic.save()

        assert Topic.objects.fetch_excluded_topics().count() == 1, 'Topic is new (just updated), so should be excluded'

        excluded_topic = Topic.objects.fetch_excluded_topics().first()

        assert excluded_topic.id == topic.id

        topic.updated = past_timestamp
        topic.posts_count = 15
        topic.save()

        assert Topic.objects.fetch_excluded_topics().count() == 1, 'Topic should be excluded because posts ' \
                                                                   'count on/above maximum'

        topic.updated = past_timestamp
        topic.posts_count = 1
        topic.views_count = 2000
        topic.save()

        assert Topic.objects.fetch_excluded_topics().count() == 1, 'Topic should be excluded because views ' \
                                                                   'count on/above maximum'

        topic.updated = past_timestamp
        topic.posts_count = 1
        topic.views_count = 1
        topic.closed = True
        topic.save()

        assert Topic.objects.fetch_excluded_topics().count() == 1, 'Topic should be excluded because it is ' \
                                                                   'closed'

        topic.updated = past_timestamp
        topic.posts_count = 1
        topic.views_count = 1
        topic.closed = False
        topic.location = None
        # validation turned off because insertion method in adapter uses direct write via Pymongo
        # without validation check
        topic.save(validate=False)

        assert Topic.objects.fetch_excluded_topics().count() == 1, 'Topic should be excluded because there is ' \
                                                                   'no location'

        topic.updated = past_timestamp
        topic.posts_count = 1
        topic.views_count = 1
        topic.closed = False
        topic.location = 'киев'
        topic.save()

        assert Topic.objects.fetch_excluded_topics().count() == 0, 'There is no reason to exclude topic'
