import asyncio
from typing import Optional, Union

import pytest


class RequestAsyncContextManager:

    def __init__(
            self, content_type: Optional[str], result: Optional[Union[str, dict]] = None, raise_error: bool = False,
            exception=asyncio.exceptions.TimeoutError
    ):
        self.content_type = content_type
        self.result = result
        self.raise_error = raise_error
        self.exception = exception

    def __await__(self):
        return iter([self])

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        await asyncio.sleep(0)

    async def text(self):
        if not self.raise_error:
            return self.result
        raise self.exception()

    async def json(self):
        if not self.raise_error:
            return self.result
        raise self.exception()


@pytest.fixture
def create_async_request_context_manager():
    def inner(content_type='html/text', result=None, raise_error=False, exception=asyncio.exceptions.TimeoutError):
        return RequestAsyncContextManager(content_type, result, raise_error, exception)
    return inner
