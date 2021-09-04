from datetime import datetime, timedelta

from mongoengine.queryset import Q, QuerySet


class AuthorQuerySet(QuerySet):

    def create_or_update(self, nickname: str, profile_link: str):
        """
        Create or update Author record and return it back to caller.
        This used in topics bulk upsert/update logic.
        """
        self(nickname=nickname).update(set__profile_link=profile_link, upsert=True)
        return self.get(nickname=nickname)


class TopicQuerySet(QuerySet):

    def fetch_excluded_topics(
            self, max_posts_count: int = 15, max_views_count: int = 2000, time_limit: int = 15
    ):
        """
        Return Topic ID's that needs to be excluded (no requests for topic page content scrapping)
        """
        date_limit = datetime.utcnow() - timedelta(minutes=time_limit)
        return self.filter(
            Q(posts_count__gte=max_posts_count) |
            Q(views_count__gte=max_views_count) |
            Q(updated__gte=date_limit) |
            Q(closed=True) |
            Q(location=None)
        ).only('topic_id')
