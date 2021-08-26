import datetime

from mongoengine import Document, StringField, URLField, IntField, ReferenceField, DateTimeField, BooleanField

from .managers import AuthorQuerySet, TopicQuerySet


class TimestampedDocument(Document):

    meta = {'allow_inheritance': True, 'abstract': True}

    created = DateTimeField(required=True, default=datetime.datetime.now)
    updated = DateTimeField(required=True, default=datetime.datetime.now)

    def save(
        self,
        force_insert=False,
        validate=True,
        clean=True,
        write_concern=None,
        cascade=None,
        cascade_kwargs=None,
        _refs=None,
        save_condition=None,
        signal_kwargs=None,
        **kwargs,
    ):
        self.updated = datetime.datetime.now()
        super().save(
            force_insert, validate, clean, write_concern, cascade, cascade_kwargs, _refs, save_condition,
            signal_kwargs, **kwargs
        )


class Author(Document):
    meta = {'queryset_class': AuthorQuerySet, 'collection': 'Authors'}

    nickname = StringField(required=True, max_length=128)
    profile_link = URLField(required=True)


class Topic(TimestampedDocument):

    meta = {'queryset_class': TopicQuerySet, 'collection': 'Topics'}

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
