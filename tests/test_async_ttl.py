import asyncio
from unittest.mock import patch

import pytest

from cached_property import cached_property_with_ttl


def test_async_ttl_reuses_task_and_refreshes_after_expiry():
    class Example:
        calls = 0

        @cached_property_with_ttl(ttl=5)
        async def value(self):
            self.calls += 1
            await asyncio.sleep(0)
            return self.calls

    async def exercise():
        obj = Example()
        with patch("cached_property.time", return_value=100):
            first = obj.value
            assert await first == 1
            assert obj.value is first
            assert await obj.value == 1
        with patch("cached_property.time", return_value=106):
            second = obj.value
            assert second is not first
            assert await asyncio.gather(second, obj.value) == [2, 2]
            assert obj.calls == 2
            del obj.value
            assert await obj.value == 3

    asyncio.run(exercise())


def test_async_ttl_retains_exception_until_expiry():
    class Example:
        @cached_property_with_ttl(ttl=5)
        async def value(self):
            raise ValueError("failed computation")

    async def exercise():
        obj = Example()
        with patch("cached_property.time", return_value=100):
            for _ in range(2):
                with pytest.raises(ValueError, match="failed computation"):
                    await obj.value

    asyncio.run(exercise())
