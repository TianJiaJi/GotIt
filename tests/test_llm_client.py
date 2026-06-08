import json
import unittest

from src.core.llm_client import (
    OpenAICompatibleClient,
    chat_completions_url,
    is_local_api,
    normalize_model_name,
)


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"content": "模型回答"}}]}
        ).encode("utf-8")


class LLMClientTests(unittest.TestCase):
    def test_builds_provider_endpoint(self):
        self.assertEqual(
            chat_completions_url("https://api.deepseek.com"),
            "https://api.deepseek.com/chat/completions",
        )
        self.assertEqual(
            chat_completions_url("https://api.openai.com/v1/"),
            "https://api.openai.com/v1/chat/completions",
        )

    def test_normalizes_legacy_provider_prefix(self):
        self.assertEqual(
            normalize_model_name("deepseek/deepseek-chat", "https://api.deepseek.com"),
            "deepseek-chat",
        )

    def test_local_api_does_not_require_key(self):
        self.assertTrue(is_local_api("http://127.0.0.1:11434/v1"))

    def test_complete_parses_openai_compatible_response(self):
        captured = {}

        def opener(request, timeout):
            captured["url"] = request.full_url
            captured["timeout"] = timeout
            captured["payload"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse()

        client = OpenAICompatibleClient(timeout=12, opener=opener)
        answer = client.complete(
            model="deepseek-v4-flash",
            messages=[{"role": "user", "content": "你好"}],
            api_key="secret",
            api_base="https://api.deepseek.com",
            temperature=0.3,
            max_tokens=100,
        )

        self.assertEqual(answer, "模型回答")
        self.assertEqual(captured["timeout"], 12)
        self.assertEqual(captured["payload"]["model"], "deepseek-v4-flash")
        self.assertEqual(captured["payload"]["thinking"], {"type": "disabled"})
