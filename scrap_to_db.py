from scrapper.engine.over_scrapper import OverclockersScrapper
from scrapper.models.adapters import Topic, TopicsToDBAdapter


if __name__ == '__main__':
    scrapper = OverclockersScrapper()
    topics = scrapper.get_topics(1, 10)

    adapter = TopicsToDBAdapter()
    adapter.connect()

    # excluding some topics to avoid firing redundant requests
    topics_to_exclude = [topic.topic_id for topic in Topic.objects.fetch_excluded_topics()]  # pylint: disable=no-member
    topics = list(filter(lambda topic: topic.topic_id not in topics_to_exclude, topics))
    topics_mapping = {t.topic_id: t for t in topics}

    topics_data = scrapper.get_topics_content([(t.url, {}) for t in topics])
    for topic in topics_data:
        topic_meta = topics_mapping.get(topic.topic_id)
        topic_meta.topic_content = topic.content
        topic_meta.closed = topic.closed

    result = adapter.import_topics_to_db(list(topics_mapping.values()))
    if result:
        modified_records = result.modified_count
        upserted_records = result.upserted_count
        inserted_records = result.inserted_count

        print(f'Excluded: {len(topics_to_exclude)}\nModified: {modified_records}\nUpserted: {upserted_records}\n'
              f'Inserted: {inserted_records}')
    else:
        print('No updates')
