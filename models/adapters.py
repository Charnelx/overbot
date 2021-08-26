from collections import defaultdict
from typing import List

from mongoengine import connect
import pymongo

from scrapper.engine.base import TopicMetaInfo
from scrapper.settings import settings
from scrapper.models.overclockers_models import Author, Topic


class TopicsToDBAdapter:

    def __init__(self):
        self.connection = None

    def connect(self):
        db_settings = settings.SCRAPPER_DATABASES['default']
        self.connection = connect(
            db=db_settings.get('db_name'),
            host=db_settings.get('host'),
            port=db_settings.get('port')
        )

    def import_topics_to_db(self, topics: List[TopicMetaInfo]):
        authors_mapping = defaultdict(list)
        # trick for optimization - allows to create/update author
        # only one's for a group of topics
        for topic in topics:
            authors_mapping[topic.author].append(topic)

        topics_bulk = []
        for author, topic_list in authors_mapping.items():
            author_record = Author.objects.create_or_update(
                nickname=author, profile_link=topic_list[0].author_profile_link
            )

            for topic in topic_list:
                topic_data = topic.to_json()
                topic_data['author'] = author_record
                topics_bulk.append(Topic(**topic_data))

        # bulk upsert/update
        operations = [
            pymongo.ReplaceOne({'topic_id': topic.topic_id}, topic.to_mongo(), upsert=True)
            for topic in topics_bulk
        ]
        result = Topic._get_collection().bulk_write(operations)
        return result
