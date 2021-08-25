from selectolax.parser import HTMLParser

from .base import TopicMetaInfo, TopicData


class OverclockersParser:

    def __init__(self, domain):
        self.domain = domain

    def parse_topics_list(self, page_content: str):
        results = []

        root = HTMLParser(page_content)
        topic_parent_elements = root.css('.bg1,.bg2')
        for element in topic_parent_elements:
            topic_href_element = element.css_first('.topictitle')
            topic_title = topic_href_element.text()

            rel_url = topic_href_element.attributes.get('href')

            author = element.css_first('.author > a').text()
            author_profile_rel_url = element.css_first('.author > a').attributes.get('href')
            answers = element.css_first('.posts').child.html
            views = element.css_first('.views').child.html
            last_post_dt_string = element.css_first('.lastpost span time').attributes.get('datetime')

            data_container = TopicMetaInfo(
                domain=self.domain,
                topic_id=0,
                url=rel_url,
                title=topic_title,
                author=author,
                author_profile_link=author_profile_rel_url,
                posts_count=answers,
                views_count=views,
                last_post_timestamp=last_post_dt_string
            )
            data_container.process()

            results.append(data_container)
        return results

    def parse_topic_content(self, page_content: str, url: str):
        root = HTMLParser(page_content)
        topic_content = root.css_first('.bg1 > .inner > .postbody > * > .content').text()

        data_container = TopicData(
            content=topic_content,
            url=url
        )

        data_container.process()
        return data_container
