"""AI answer generation through LiteLLM."""

from __future__ import annotations

import json
import os
from collections.abc import Callable
from typing import Any

from .llm_client import OpenAICompatibleClient, is_local_api


class AIAnswerManager:
    """Generate short structured answers for OCR text."""

    def __init__(
        self,
        config_manager=None,
        completion_fn: Callable[..., Any] | None = None,
        client: OpenAICompatibleClient | None = None,
    ):
        self.config_manager = config_manager
        self._completion_fn = completion_fn
        self.client = client or OpenAICompatibleClient()
        self._initialized = False
        self.reload_config()
        self.system_prompt = self._get_system_prompt()

    def reload_config(self) -> None:
        if self.config_manager:
            config = self.config_manager.get_ai_config()
            self.model_name = config["model"].strip()
            self.api_key = config["api_key"].strip()
            self.api_base = config["api_base"].strip()
            self.temperature = config["temperature"]
            self.max_tokens = config["max_tokens"]
        else:
            self.model_name = os.getenv("GOTIT_MODEL", "deepseek-v4-flash")
            self.api_key = os.getenv("GOTIT_API_KEY", "")
            self.api_base = os.getenv("GOTIT_API_BASE", "https://api.deepseek.com")
            self.temperature = 0.3
            self.max_tokens = 400

    @staticmethod
    def _get_system_prompt() -> str:
        return """你是一个快速、准确的答题助手。
只返回合法 JSON，不要包含 Markdown 标记或解释过程：
{"status":"success","answer":"最终答案"}
选择题返回“选项字母. 选项内容”，判断题返回“正确”或“错误”。
如果文本不是有效题目，返回：
{"status":"error","answer":"未识别到有效题目，请重新截图"}
答案尽量控制在 80 个字符以内。"""

    def init_ai(self) -> bool:
        self._initialized = True
        return True

    def _completion(self, **kwargs):
        if self._completion_fn:
            return self._completion_fn(**kwargs)
        return self.client.complete(**kwargs)

    @staticmethod
    def _response_text(response) -> str:
        if isinstance(response, str):
            return response
        return response.choices[0].message.content

    @staticmethod
    def parse_response(answer_text: str) -> dict[str, str]:
        text = (answer_text or "").strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines:
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines.pop()
            text = "\n".join(lines).strip()

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                try:
                    parsed = json.loads(text[start : end + 1])
                except json.JSONDecodeError:
                    parsed = None
            else:
                parsed = None

        if isinstance(parsed, dict) and isinstance(parsed.get("answer"), str):
            status = parsed.get("status", "success")
            if status not in {"success", "error"}:
                status = "success"
            return {"status": status, "answer": parsed["answer"].strip()}

        if text:
            return {"status": "success", "answer": text}
        return {"status": "error", "answer": "AI未返回内容"}

    def get_answer(self, question_text: str) -> dict[str, str]:
        if not question_text or not question_text.strip() or question_text.startswith("["):
            return {"status": "error", "answer": "未识别到有效题目，请重新截图"}
        if not self.is_available():
            return {"status": "error", "answer": "请先配置AI模型和API密钥"}
        if not self._initialized:
            self.init_ai()

        try:
            response = self._completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question_text},
                ],
                api_key=self.api_key,
                api_base=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return self.parse_response(self._response_text(response))
        except Exception as exc:
            print(f"AI答题失败: {exc}")
            return {"status": "error", "answer": f"AI调用失败: {exc}"}

    def is_available(self) -> bool:
        if not self.model_name:
            return False
        return bool(self.api_key) or is_local_api(self.api_base)

    def set_model_config(self, model_name: str, api_key: str = "", api_base: str = "") -> bool:
        self.model_name = model_name.strip()
        self.api_key = api_key.strip()
        self.api_base = api_base.strip()
        return True
