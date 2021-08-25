from scrapper.engine.over_scrapper import OverclockersScrapper


if __name__ == '__main__':
    scrapper = OverclockersScrapper()
    topics = scrapper.get_topics(1, 5)
    topics_mapping = {t.topic_id: t for t in topics}

    # TODO: add logic - no need to request topic content if topic is not updated
    # TODO: or we don't need this topic
    topics_data = scrapper.get_topics_content([(t.url, dict()) for t in topics])
    for topic in topics_data:
        topic_meta = topics_mapping.get(topic.topic_id)
        topic_meta.content = topic.content

    for topic in topics_mapping.values():
        print(topic.location, topic.location_raw)