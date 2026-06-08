import unittest
from types import SimpleNamespace

from src.core.ai_answer import AIAnswerManager


class StubConfig:
    def get_ai_config(self):
        return {
            "model": "deepseek-v4-flash",
            "api_key": "secret",
            "api_base": "https://example.test",
            "temperature": 0.3,
            "max_tokens": 400,
        }


class AIAnswerManagerTests(unittest.TestCase):
    def test_parses_json_inside_markdown(self):
        parsed = AIAnswerManager.parse_response(
            '```json\n{"status":"success","answer":"B. 2"}\n```'
        )
        self.assertEqual(parsed, {"status": "success", "answer": "B. 2"})

    def test_plain_text_response_remains_usable(self):
        self.assertEqual(
            AIAnswerManager.parse_response("北京"),
            {"status": "success", "answer": "北京"},
        )

    def test_completion_result_is_normalized(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"answer":"正确"}'))]
        )
        manager = AIAnswerManager(StubConfig(), completion_fn=lambda **_kwargs: response)

        self.assertEqual(
            manager.get_answer("地球围绕太阳转"),
            {"status": "success", "answer": "正确"},
        )
