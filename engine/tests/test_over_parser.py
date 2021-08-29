# pylint: disable=no-self-use

from datetime import datetime, timezone

from scrapper.engine.over_parser import OverclockersParser


class TestOverclockersParser:

    def test_parse_topics_list(self):
        html = '''
        <li class="row bg1">
            <dl class="row-item topic_unread">
                <dt>
                    <a href="./viewtopic.php?f=26&t=1234567890" class="topictitle">
                    [Украина, Киев] Видеокарта с функцией скороварки 
                    </a>
                </dt>
                <dd class="author">
                    <a href="./memberlist.php?mode=viewprofile&u=12345" class="username"> Vasyan2000 </a>
                </dd>
                <dd class="posts">3 </dd>
                <dd class="views">100 </dd>
                <dd class="lastpost">
                    <span>
                        <br>
                        <time datetime="2021-08-29T15:17:40+00:00"></time>
                    </span>
                </dd>
            </dl>
        </li>'''

        parser = OverclockersParser(domain='https://forum.overclockers.ua')
        result = parser.parse_topics_list(page_content=html)

        assert len(result) == 1

        topic_meta_info = result[0]

        assert topic_meta_info.topic_id == 1234567890
        assert topic_meta_info.url == 'https://forum.overclockers.ua/viewtopic.php?f=26&t=1234567890'
        assert topic_meta_info.title == 'Видеокарта с функцией скороварки'
        assert topic_meta_info.posts_count == 3
        assert topic_meta_info.views_count == 100
        assert topic_meta_info.author == 'Vasyan2000'
        assert topic_meta_info.author_profile_link == \
               'https://forum.overclockers.ua/memberlist.php?mode=viewprofile&u=12345'
        assert topic_meta_info.location == 'киев'
        assert topic_meta_info.location_raw == 'Украина, Киев'
        assert topic_meta_info.closed is False
        assert topic_meta_info.processed is True
        assert topic_meta_info.last_post_timestamp == datetime(2021, 8, 29, 15, 17, 40, tzinfo=timezone.utc)

    def test_parse_topic_content(self):
        html = '''
        <div class="some bg1">
            <div class="inner">
                <div class="postbody">
                    <div class="post_content1234567890">
                        <div class="content">Продается кофеварка со встроенной майнинг-фермой и PS4 china edition
                        Недорого - 19999,9 коинов 
                        </div>
                    </div>
                </div>
            </div>
        </div>'''

        parser = OverclockersParser(domain='https://forum.overclockers.ua')
        result = parser.parse_topic_content(
            page_content=html,
            url='https://forum.overclockers.ua/viewtopic.php?f=26&t=1234567890'
        )

        assert result.topic_id == 1234567890
        assert result.url == 'https://forum.overclockers.ua/viewtopic.php?f=26&t=1234567890'
        assert result.closed is False
        assert result.content.strip() == 'Продается кофеварка со встроенной майнинг-фермой и PS4 china edition\n' \
            '                        Недорого - 19999,9 коинов'

    def test_parse_topic_content_closed(self):
        html = '''
        <div class="some bg1">
            <div class="fa-lock"></div>
            <div class="inner">
                <div class="postbody">
                    <div class="post_content1234567890">
                        <div class="content">Продается кофеварка со встроенной майнинг-фермой и PS4 china edition
                        Недорого - 19999,9 коинов 
                        </div>
                    </div>
                </div>
            </div>
        </div>'''

        parser = OverclockersParser(domain='https://forum.overclockers.ua')
        result = parser.parse_topic_content(
            page_content=html,
            url='https://forum.overclockers.ua/viewtopic.php?f=26&t=1234567890'
        )

        assert result.topic_id == 1234567890
        assert result.url == 'https://forum.overclockers.ua/viewtopic.php?f=26&t=1234567890'
        assert result.closed is True
        assert result.content.strip() == 'Продается кофеварка со встроенной майнинг-фермой и PS4 china edition\n' \
            '                        Недорого - 19999,9 коинов'
