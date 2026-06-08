import json
import tempfile
import unittest
from pathlib import Path

from src.config.config import ConfigManager


class ConfigManagerTests(unittest.TestCase):
    def test_load_merges_new_defaults_without_losing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps({"ai": {"api_key": "secret"}, "display": {"show_result_popup": False}}),
                encoding="utf-8",
            )

            manager = ConfigManager(path)

            self.assertEqual(manager.get_ai_config()["api_key"], "secret")
            self.assertEqual(manager.get_ai_config()["model"], "deepseek-v4-flash")
            self.assertFalse(manager.get_display_config()["show_result_popup"])
            self.assertIn("capture", manager.config)

    def test_region_and_empty_api_key_can_be_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            manager = ConfigManager(path)
            manager.update_ai_config(api_key="secret")
            manager.update_ai_config(api_key="")
            manager.update_capture_config(region=(10, 20, 300, 400))

            reloaded = ConfigManager(path)

            self.assertEqual(reloaded.get_ai_config()["api_key"], "")
            self.assertEqual(reloaded.get_capture_config()["region"], [10, 20, 300, 400])
