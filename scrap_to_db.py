from scrapper.engine.over_scrapper import OverclockersScrapper
from scrapper.models.adapters import Topic, TopicsToDBAdapter


if __name__ == '__main__':
    scrapper = OverclockersScrapper()
    topics = scrapper.get_topics(1, 5)

    adapter = TopicsToDBAdapter()
    adapter.connect()

    # excluding some topics to avoid firing redundant requests
    topics_to_exclude = [topic.topic_id for topic in Topic.objects.fetch_excluded_topics()]
    topics = list(filter(lambda topic: False if topic.topic_id in topics_to_exclude else True, topics))
    topics_mapping = {t.topic_id: t for t in topics}

    topics_data = scrapper.get_topics_content([(t.url, dict()) for t in topics])
    for topic in topics_data:
        topic_meta = topics_mapping.get(topic.topic_id)
        topic_meta.topic_content = topic.content

    result = adapter.import_topics_to_db(list(topics_mapping.values()))
    modified_records = result.modified_count
    upserted_records = result.upserted_count
    inserted_records = result.inserted_count

    print(f'Modified: {modified_records}\nUpserted: {upserted_records}\nInserted: {inserted_records}')
