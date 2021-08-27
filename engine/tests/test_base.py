import pytest

from scrapper.engine.base import BaseScraper, ScrapperMixin


class TestBaseScrapper:

    def test_inherited_without_class_attrs(self):
        class Subclass(BaseScraper):
            pass

        with pytest.raises(TypeError):
            inst = Subclass()


class TestScrapperMixin:

    def test_headers_partial_call(self):
        mixin = ScrapperMixin()
        mixin.DOMAIN = 'some_domain'
        mixin.HOST = 'some_host'

        assert mixin._headers_partial == {'Host': 'some_host', 'Referer': 'some_domain'}

    def test_generate_headers(self):
        mixin = ScrapperMixin()
        mixin.DOMAIN = 'other_domain'
        mixin.HOST = 'other_host'

        headers = mixin.generate_headers()
        user_agent_header = headers.pop('User-Agent')

        assert user_agent_header is not None
        assert headers == {'Host': 'other_host', 'Referer': 'other_domain'}
