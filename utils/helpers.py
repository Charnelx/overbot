from contextlib import asynccontextmanager

import asyncio


@asynccontextmanager
async def fake_semaphore():
    try:
        yield None
    finally:
        await asyncio.sleep(0)
