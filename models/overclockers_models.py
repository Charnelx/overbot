from mongoengine import Document, StringField, URLField, IntField, ReferenceField, DateTimeField, BooleanField

from .managers import AuthorQuerySet, TopicQuerySet


class Author(Document):
    meta = {'queryset_class': AuthorQuerySet, 'collection': 'Authors'}

    nickname = StringField(required=True, max_length=128)
    profile_link = URLField(required=True)


class Topic(Document):

    meta = {'queryset_class': TopicQuerySet, 'collection': 'Topics'}

    created = DateTimeField(required=True)
    updated = DateTimeField(required=True)
    topic_id = IntField(required=True, unique=True)
    url = URLField(required=True)
    title = StringField(required=True, max_length=255)
    author = ReferenceField(Author)
    posts_count = IntField(default=0)
    views_count = IntField(default=0)
    last_post_timestamp = DateTimeField(null=True)
    location_raw = StringField(max_length=128)
    location = StringField(required=True, max_length=128)
    topic_content = StringField(required=True)
    closed = BooleanField(required=True, default=False)
