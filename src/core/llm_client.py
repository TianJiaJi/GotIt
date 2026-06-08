"""Small OpenAI-compatible chat completion client."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse


def normalize_model_name(model: str, api_base: str) -> str:
    """Strip legacy provider prefixes when talking to a provider directly."""
    value = model.strip()
    host = urlparse(api_base).hostname or ""
    if host.endswith("deepseek.com") and value.startswith("deepseek/"):
        return value.split("/", 1)[1]
    if host.endswith("openai.com") and value.startswith("openai/"):
        return value.split("/", 1)[1]
    return value


def chat_completions_url(api_base: str) -> str:
    base = api_base.strip().rstrip("/")
    if not base:
        raise ValueError("API 地址不能为空")
    if base.endswith("/chat/completions"):
        return base
    return f"{base}/chat/completions"


def is_local_api(api_base: str) -> bool:
    host = (urlparse(api_base).hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1"}


class OpenAICompatibleClient:
    """Call non-streaming chat completions using only the standard library."""

    def __init__(self, timeout: int = 90, opener=None):
        self.timeout = timeout
        self.opener = opener or urllib.request.urlopen

    def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        api_key: str,
        api_base: str,
        temperature: float,
        max_tokens: int,
    ) -> str:
        payload = {
            "model": normalize_model_name(model, api_base),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        host = (urlparse(api_base).hostname or "").lower()
        if host.endswith("deepseek.com") and payload["model"].startswith("deepseek-v4"):
            payload["thinking"] = {"type": "disabled"}
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        request = urllib.request.Request(
            chat_completions_url(api_base),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with self.opener(request, timeout=self.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            try:
                detail = exc.read().decode("utf-8")
            except Exception:
                detail = str(exc)
            raise RuntimeError(f"模型服务返回 HTTP {exc.code}: {detail[:300]}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"无法连接模型服务: {exc.reason}") from exc
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"模型服务响应无效: {exc}") from exc

        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("模型服务未返回有效回答") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("模型服务返回了空回答")
        return content.strip()
