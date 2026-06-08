"""Application configuration management."""

from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = {
    "app": {
        "name": "截图答题工具",
        "version": "1.1.0",
    },
    "hotkey": {
        "modifiers": "alt+shift",
        "key": "q",
    },
    "ai": {
        "model": "deepseek-v4-flash",
        "api_key": "",
        "api_base": "https://api.deepseek.com",
        "temperature": 0.3,
        "max_tokens": 400,
    },
    "ocr": {
        "language": "auto",
        "confidence_threshold": 0.5,
    },
    "capture": {
        "hide_window": True,
        "delay_ms": 300,
        "region": None,
    },
    "display": {
        "show_result_popup": True,
        "notifications_enabled": True,
    },
}


def _deep_merge(defaults: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
    """Return values merged over defaults without sharing nested objects."""
    merged = copy.deepcopy(defaults)
    for key, value in values.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


class ConfigManager:
    """Load, validate and persist the application configuration."""

    def __init__(self, config_file: str | os.PathLike[str] | None = None):
        project_root = Path(__file__).resolve().parents[2]
        self.config_file = Path(config_file) if config_file else project_root / "config" / "config.json"
        self.default_config = copy.deepcopy(DEFAULT_CONFIG)
        self.config: dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> dict[str, Any]:
        """Load configuration and fill fields introduced by newer versions."""
        loaded: dict[str, Any] = {}
        if self.config_file.exists():
            try:
                with self.config_file.open("r", encoding="utf-8") as file:
                    parsed = json.load(file)
                if isinstance(parsed, dict):
                    loaded = parsed
            except (json.JSONDecodeError, OSError) as exc:
                print(f"配置文件读取失败: {exc}，使用默认配置")

        self.config = _deep_merge(self.default_config, loaded)
        self._normalize()

        if self.config != loaded:
            self.save_config()
        return copy.deepcopy(self.config)

    def _normalize(self) -> None:
        ai = self.config["ai"]
        ai["temperature"] = min(2.0, max(0.0, self._as_float(ai.get("temperature"), 0.3)))
        ai["max_tokens"] = max(1, self._as_int(ai.get("max_tokens"), 400))

        ocr = self.config["ocr"]
        ocr["confidence_threshold"] = min(
            1.0,
            max(0.0, self._as_float(ocr.get("confidence_threshold"), 0.5)),
        )

        capture = self.config["capture"]
        capture["delay_ms"] = min(5000, max(0, self._as_int(capture.get("delay_ms"), 300)))
        region = capture.get("region")
        if not (
            isinstance(region, list)
            and len(region) == 4
            and all(isinstance(value, (int, float)) for value in region)
        ):
            capture["region"] = None

    @staticmethod
    def _as_float(value: Any, fallback: float) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return fallback

    @staticmethod
    def _as_int(value: Any, fallback: int) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return fallback

    def save_config(self) -> None:
        """Atomically save the current configuration."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.config_file.parent,
                prefix=f".{self.config_file.name}.",
                suffix=".tmp",
                delete=False,
            ) as file:
                json.dump(self.config, file, indent=2, ensure_ascii=False)
                temp_path = Path(file.name)
            temp_path.replace(self.config_file)
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink()

    def get_hotkey_config(self) -> tuple[str, str]:
        hotkey = self.config["hotkey"]
        return hotkey["modifiers"], hotkey["key"]

    def update_hotkey_config(self, modifiers: str, key: str) -> None:
        self.config["hotkey"].update({"modifiers": modifiers, "key": key})
        self.save_config()

    def get_ai_config(self) -> dict[str, Any]:
        return copy.deepcopy(self.config["ai"])

    def update_ai_config(
        self,
        model: str | None = None,
        api_key: str | None = None,
        api_base: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        updates = {
            "model": model,
            "api_key": api_key,
            "api_base": api_base,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        self.config["ai"].update({key: value for key, value in updates.items() if value is not None})
        self._normalize()
        self.save_config()

    def get_ocr_config(self) -> dict[str, Any]:
        return copy.deepcopy(self.config["ocr"])

    def update_ocr_config(
        self,
        language: str | None = None,
        confidence_threshold: float | None = None,
    ) -> None:
        if language is not None:
            self.config["ocr"]["language"] = language
        if confidence_threshold is not None:
            self.config["ocr"]["confidence_threshold"] = confidence_threshold
        self._normalize()
        self.save_config()

    def get_capture_config(self) -> dict[str, Any]:
        return copy.deepcopy(self.config["capture"])

    def update_capture_config(
        self,
        hide_window: bool | None = None,
        delay_ms: int | None = None,
        region: list[int] | tuple[int, int, int, int] | None = None,
        clear_region: bool = False,
    ) -> None:
        capture = self.config["capture"]
        if hide_window is not None:
            capture["hide_window"] = bool(hide_window)
        if delay_ms is not None:
            capture["delay_ms"] = delay_ms
        if clear_region:
            capture["region"] = None
        elif region is not None:
            capture["region"] = [int(value) for value in region]
        self._normalize()
        self.save_config()

    def get_app_info(self) -> dict[str, Any]:
        return copy.deepcopy(self.config["app"])

    def get_display_config(self) -> dict[str, Any]:
        return copy.deepcopy(self.config["display"])

    def update_display_config(
        self,
        show_result_popup: bool | None = None,
        notifications_enabled: bool | None = None,
    ) -> None:
        if show_result_popup is not None:
            self.config["display"]["show_result_popup"] = bool(show_result_popup)
        if notifications_enabled is not None:
            self.config["display"]["notifications_enabled"] = bool(notifications_enabled)
        self.save_config()
