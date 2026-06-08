"""Context-aware clipboard and text chat."""

from __future__ import annotations

import json
import os
import platform
import threading
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from .llm_client import OpenAICompatibleClient, is_local_api


def default_context_file() -> Path:
    system = platform.system()
    if system == "Windows":
        base = Path(os.getenv("LOCALAPPDATA", Path.home()))
    elif system == "Darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.getenv("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "GotIt" / "clipboard_context.json"


class ClipboardChatManager:
    """Persist a bounded conversation and send it through LiteLLM."""

    def __init__(
        self,
        config_manager=None,
        context_file: str | os.PathLike[str] | None = None,
        completion_fn: Callable[..., Any] | None = None,
        client: OpenAICompatibleClient | None = None,
    ):
        self.config_manager = config_manager
        self.context_file = Path(context_file) if context_file else default_context_file()
        self._completion_fn = completion_fn
        self.client = client or OpenAICompatibleClient()
        self.conversation_history: list[dict[str, str]] = []
        self.max_history = 50
        self._lock = threading.Lock()
        self.reload_config()
        self._load_context()

    def reload_config(self) -> None:
        if self.config_manager:
            config = self.config_manager.get_ai_config()
            self.model_name = config["model"].strip()
            self.api_key = config["api_key"].strip()
            self.api_base = config["api_base"].strip()
            self.temperature = min(1.2, max(0.1, float(config.get("temperature", 0.7))))
            self.max_tokens = max(200, int(config.get("max_tokens", 1200)))
        else:
            self.model_name = os.getenv("GOTIT_MODEL", "deepseek-v4-flash")
            self.api_key = os.getenv("GOTIT_API_KEY", "")
            self.api_base = os.getenv("GOTIT_API_BASE", "https://api.deepseek.com")
            self.temperature = 0.7
            self.max_tokens = 1200

    @staticmethod
    def _get_system_prompt() -> str:
        return (
            "你是一个简洁、准确的中文助手。结合最近的对话上下文回答用户，"
            "代码问题给出可直接使用的示例。直接输出回答正文。"
        )

    def _load_context(self) -> None:
        try:
            if self.context_file.exists():
                data = json.loads(self.context_file.read_text(encoding="utf-8"))
                history = data.get("history", [])
                if isinstance(history, list):
                    self.conversation_history = history[-self.max_history :]
        except (OSError, json.JSONDecodeError):
            self.conversation_history = []

    def _save_context(self) -> None:
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "history": self.conversation_history,
            "last_update": datetime.now().isoformat(timespec="seconds"),
        }
        self.context_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def clear_context(self):
        with self._lock:
            self.conversation_history = []
            try:
                self._save_context()
            except OSError as exc:
                return {"status": "error", "message": f"清空上下文失败: {exc}"}
        return {"status": "success", "message": "对话上下文已清空"}

    def _completion(self, **kwargs):
        if self._completion_fn:
            return self._completion_fn(**kwargs)
        return self.client.complete(**kwargs)

    @staticmethod
    def _response_text(response) -> str:
        if isinstance(response, str):
            return response
        return response.choices[0].message.content

    def process_clipboard_text(self, text: str):
        prompt = (text or "").strip()
        if not prompt:
            return {"status": "error", "message": "输入内容为空"}
        if not self.is_available():
            return {"status": "error", "message": "请先配置AI模型和API密钥"}

        with self._lock:
            user_message = {"role": "user", "content": prompt}
            pending_history = [*self.conversation_history, user_message]
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend(pending_history[-20:])

            try:
                response = self._completion(
                    model=self.model_name,
                    messages=messages,
                    api_key=self.api_key,
                    api_base=self.api_base,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                answer = self._response_text(response).strip()
                if not answer:
                    raise ValueError("AI未返回内容")
            except Exception as exc:
                return {"status": "error", "message": f"AI处理失败: {exc}"}

            self.conversation_history = [
                *pending_history,
                {"role": "assistant", "content": answer},
            ][-self.max_history :]
            try:
                self._save_context()
            except OSError as exc:
                return {"status": "error", "message": f"保存对话失败: {exc}"}

            return {
                "status": "success",
                "answer": answer,
                "history_count": len(self.conversation_history),
            }

    def get_context_info(self):
        return {"total_messages": len(self.conversation_history)}

    def is_available(self) -> bool:
        if not self.model_name:
            return False
        return bool(self.api_key) or is_local_api(self.api_base)
