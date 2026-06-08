import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.core.clipboard_chat import ClipboardChatManager


class StubConfig:
    def get_ai_config(self):
        return {
            "model": "deepseek-v4-flash",
            "api_key": "secret",
            "api_base": "https://example.test",
            "temperature": 0.5,
            "max_tokens": 500,
        }


class ClipboardChatManagerTests(unittest.TestCase):
    def test_failed_request_does_not_pollute_context(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = ClipboardChatManager(
                StubConfig(),
                context_file=Path(directory) / "context.json",
                completion_fn=lambda **_kwargs: (_ for _ in ()).throw(RuntimeError("offline")),
            )

            result = manager.process_clipboard_text("问题")

            self.assertEqual(result["status"], "error")
            self.assertEqual(manager.conversation_history, [])

    def test_successful_request_is_saved(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="回答"))]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "context.json"
            manager = ClipboardChatManager(
                StubConfig(),
                context_file=path,
                completion_fn=lambda **_kwargs: response,
            )

            result = manager.process_clipboard_text("问题")

            self.assertEqual(result["history_count"], 2)
            self.assertTrue(path.exists())
