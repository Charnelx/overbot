from mongoengine.errors import ValidationError
from mongomock.helpers import utcnow
import pytest

from scrapper.models.overclockers_models import Author, Topic
from scrapper.models.managers import AuthorQuerySet, TopicQuerySet


@pytest.mark.usefixtures("mocked_db_connection")
class TestOverclockersModels:

    def test_author_creation(self):
        author = Author(nickname='joedoe', profile_link='https://example.com')
        author.save()

        assert Author.objects.count() == 1

        entry_from_db = Author.objects.first()

        assert entry_from_db._meta['collection'] == 'Authors'
        assert issubclass(Author._meta['queryset_class'], AuthorQuerySet)

        assert entry_from_db.nickname == author.nickname
        assert entry_from_db.profile_link == author.profile_link

    def test_author_creation_with_broken_link(self):
        author = Author(nickname='joedoe', profile_link='example.com')

        with pytest.raises(ValidationError) as err:
            author.save()

        assert str(err.value) == "ValidationError (Author:None) (Invalid scheme example.com in URL: example.com: " \
                                 "['profile_link'])"
        assert Author.objects.count() == 0

    def test_topic_creation(self, create_author):
        author = create_author(nickname='joedoe', profile_link='https://example.com')

        timestamp = utcnow()

        topic = Topic(
            created=timestamp,
            updated=timestamp,
            topic_id=123456,
            url='https://example.com',
            title='Some topic title',
            author=author,
            posts_count=1,
            views_count=1,
            last_post_timestamp=timestamp,
            location_raw='Украина, Киев',
            location='киев',
            topic_content='some content'
        )

        topic.save()

        assert Topic.objects.count() == 1

        entry_from_db = Topic.objects.first()

        assert entry_from_db.created.replace(microsecond=0) == timestamp.replace(microsecond=0)
        assert entry_from_db.updated.replace(microsecond=0) == timestamp.replace(microsecond=0)
        assert entry_from_db.topic_id == 123456
        assert entry_from_db.url == 'https://example.com'
        assert entry_from_db.title == 'Some topic title'
        assert entry_from_db.author.id == author.id
        assert entry_from_db.posts_count == 1
        assert entry_from_db.views_count == 1
        assert entry_from_db.last_post_timestamp.replace(microsecond=0) == timestamp.replace(microsecond=0)
        assert entry_from_db.location_raw == 'Украина, Киев'
        assert entry_from_db.location == 'киев'
        assert entry_from_db.topic_content == 'some content'
        assert entry_from_db.closed is False

        assert entry_from_db._meta['collection'] == 'Topics'
        assert issubclass(Topic._meta['queryset_class'], TopicQuerySet)
