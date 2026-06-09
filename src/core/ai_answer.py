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
            self.max_tokens = 1024

    @staticmethod
    def _get_system_prompt() -> str:
        return """你是一个资深的解题专家。你的任务是分析用户提供的OCR文本，识别题目类型并给出准确答案。

【OCR识别错误纠正】
输入文本来自OCR识别，可能包含以下常见错误，请在【理解题意时】自动脑补并纠正：
- 字母与数字混淆：O → 0，l/I → 1，S → 5，B → 8 等。
- 标点符号错误：` ` ` → '，" → "，( → [ 等。
- 数学符号错误：乘号(×)与字母(x)混淆，除号(÷)识别为加号(+)或减号(-)，大于等于(≥)识别为(>)等。
- 选项格式丢失：如选项字母丢失，"苹果" 应自动理解为 "A. 苹果"。
- 公式与上下标：如 "x^2"、"H_2O" 应自动理解为标准的 "x²"、"H₂O"。
- 重复或乱码字符：如 "题目题" 应理解为 "题目"，忽略无意义的乱码。

【严格输出要求】
你必须且只能输出一个合法的 JSON 对象。绝对不要包含任何 Markdown 标记（如 ```json 或 ```）、前言、后语或解释过程。直接以 { 开头，以 } 结尾。

【JSON 结构定义】
{
  "status": "success 或 error",
  "type": "题目类型（见下方分类）",
  "answer": "最终答案（见下方格式要求）"
}

【题目类型分类 (type)】
- "single_choice": 单选题（仅有一个正确答案）
- "multiple_choice": 多选题（有两个或以上正确答案）
- "true_false": 判断题（判断对错）
- "essay": 解答题/填空题/计算题/简答题
- "unknown": 无法识别为有效题目

【答案格式要求 (answer)】
1. 单选题：返回 "选项字母. 选项内容"。例如："A. 苹果"。若选项无字母，直接返回正确内容。
2. 多选题：返回所有正确选项，按字母顺序排列，用逗号分隔。例如："A. 苹果, C. 香蕉"。
3. 判断题：统一返回 "正确" 或 "错误"。
4. 解答题/填空题：
   - 填空题：直接返回填空内容。若有多个空，用逗号分隔。
   - 计算/简答题：先给出最终结果，再简述核心步骤。格式："最终结果：xxx。步骤：1... 2..."。保持简洁，直击要点，避免长篇大论。

【异常处理】
如果输入的文本不是有效的题目、内容残缺无法作答，或OCR错误导致题目完全无法理解，请返回：
{
  "status": "error",
  "type": "unknown",
  "answer": "未识别到有效题目或题目信息不全，请重新截图"
}

【注意事项】
1. 若题目包含多个小题，请在 answer 中用分号（;）分隔各小题的答案。
2. 答案必须准确、客观，符合学术规范。
3. 优先理解题意而非纠结OCR错误，但关键数字、公式、选项必须准确。
4. 再次强调：只输出纯 JSON 字符串，不要输出任何额外字符。"""

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
            result = {
                "status": status,
                "answer": parsed["answer"].strip(),
                "type": parsed.get("type", "unknown")
            }
            return result

        if text:
            return {"status": "success", "answer": text, "type": "unknown"}
        return {"status": "error", "answer": "AI未返回内容", "type": "unknown"}

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
