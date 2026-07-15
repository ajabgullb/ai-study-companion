"""Regression tests for cache backends."""

import unittest

from app.core.cache import ValkeyCacheService


class _TextValkeyClient:
  async def get(self, key: str) -> str:
    return "cached value"


class ValkeyCacheServiceTests(unittest.IsolatedAsyncioTestCase):
  async def test_get_returns_text_from_decode_responses_client(self) -> None:
    cache = ValkeyCacheService()
    cache._client = _TextValkeyClient()  # type: ignore[assignment]

    value = await cache.get("test-key")

    self.assertEqual(value, "cached value")

