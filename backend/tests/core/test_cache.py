"""Regression tests for cache backends."""

import unittest

from langchain_core.messages import BaseMessage, SystemMessage

from app.core.cache import ValkeyCacheService
from app.schemas import Message
from app.utils.graph import prepare_messages


class _TextValkeyClient:
  async def get(self, key: str) -> str:
    return "cached value"


class PrepareMessagesTests(unittest.TestCase):
  def test_returns_only_langchain_messages(self) -> None:
    prepared = prepare_messages(
      [
        Message(role="user", content="hello"),
        Message(role="assistant", content="hi"),
      ],
      "system instructions",
    )

    self.assertTrue(all(isinstance(message, BaseMessage) for message in prepared))
    self.assertIsInstance(prepared[0], SystemMessage)
    self.assertEqual(prepared[0].content, "system instructions")


class ValkeyCacheServiceTests(unittest.IsolatedAsyncioTestCase):
  async def test_get_returns_text_from_decode_responses_client(self) -> None:
    cache = ValkeyCacheService()
    cache._client = _TextValkeyClient()  # type: ignore[assignment]

    value = await cache.get("test-key")

    self.assertEqual(value, "cached value")

