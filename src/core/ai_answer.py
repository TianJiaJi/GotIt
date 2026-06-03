"""AI答题模块"""
import os
import json
from litellm import completion


class AIAnswerManager:
    """AI答题管理器"""

    def __init__(self, config_manager=None):
        # 如果传入config_manager，则从配置获取参数
        if config_manager:
            ai_config = config_manager.get_ai_config()
            self.model_name = ai_config['model']
            self.api_key = ai_config['api_key']
            self.api_base = ai_config['api_base']
            self.temperature = ai_config.get('temperature', 0.3)
            self.max_tokens = ai_config.get('max_tokens', 200)
        else:
            # 默认配置（直接读取环境变量）
            self.model_name = os.getenv("LITELLM_MODEL", "deepseek/deepseek-chat")
            self.api_key = os.getenv("LITELLM_API_KEY", "")
            self.api_base = os.getenv("LITELLM_API_BASE", "https://api.deepseek.com")
            self.temperature = 0.3
            self.max_tokens = 200

        self.system_prompt = self._get_system_prompt()
        self.init_ai()

    def _get_system_prompt(self):
        """获取系统提示词"""
        return """# Role
你是一个极速、精准的"直接给答案"助手。你的唯一任务是：阅读用户通过 OCR 识别的文本（通常是题目），并直接输出最终答案。

# Constraints (绝对红线)
1. **禁止任何推理**：绝对不要输出解题步骤、分析过程、思考过程或任何解释性文字。
2. **禁止任何废话**：不要输出"答案是"、"选"、"答："等前缀，直接给出核心结果。
3. **极简输出**：答案必须极其精炼，适合在系统右下角的小弹窗中一眼看完（控制在 50 个字符以内）。
   - 如果是选择题，直接输出"选项字母. 选项内容"（如：B. 2）。
   - 如果是判断题，直接输出"正确"、"错误"（或"对"、"错"，尽量与题目选项保持一致）。
4. **严格 JSON**：必须且只能输出合法的 JSON 字符串，不要包含 ```json 等 Markdown 标记。

# Output Format
严格遵循以下 JSON 结构：
{
  "status": "success" 或 "error",
  "answer": "最终答案。"
}

# Rules for Error Handling
- 如果 OCR 文本完全是乱码、无意义字符，或者明显无法构成一个问题，请返回：
  {"status": "error", "answer": "未识别到有效题目，请重新截图"}
- 如果题目缺少关键条件无法解答，请返回：
  {"status": "error", "answer": "题目条件不足，无法解答"}

# Examples
User: "1+1等于几？ A. 1 B. 2 C. 3"
Assistant: {"status": "success", "answer": "B. 2"}

User: "地球围绕太阳转。 (判断题)"
Assistant: {"status": "success", "answer": "正确"}

User: "水在标准大气压下50度沸腾。 A. 对 B. 错"
Assistant: {"status": "success", "answer": "B. 错"}

User: "中国的首都是哪里？"
Assistant: {"status": "success", "answer": "北京"}

User: "asdfghjkl 12345"
Assistant: {"status": "error", "answer": "未识别到有效题目，请重新截图"}"""

    def init_ai(self):
        """初始化AI引擎"""
        try:
            print(f"AI初始化成功，使用模型: {self.model_name}")
            return True
        except Exception as e:
            print(f"AI初始化失败: {e}")
            return False

    def get_answer(self, question_text):
        """获取题目答案"""
        if not question_text or not question_text.strip():
            return {"status": "error", "answer": "未识别到有效题目，请重新截图"}

        try:
            print(f"开始AI答题，问题: {question_text[:100]}...")

            # 调用LiteLLM
            response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": question_text}
                ],
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # 提取回答内容
            answer_text = response.choices[0].message.content.strip()
            print(f"AI原始回答: {answer_text}")

            # 尝试解析JSON
            try:
                # 移除可能的markdown标记
                if answer_text.startswith("```json"):
                    answer_text = answer_text.replace("```json", "").replace("```", "").strip()
                elif answer_text.startswith("```"):
                    answer_text = answer_text.replace("```", "").strip()

                result = json.loads(answer_text)

                # 验证JSON结构
                if "status" not in result or "answer" not in result:
                    print(f"AI返回的JSON格式不正确: {result}")
                    return {"status": "error", "answer": "AI返回格式错误"}

                print(f"AI解析结果: {result}")
                return result

            except json.JSONDecodeError as je:
                print(f"JSON解析失败: {je}, 原始文本: {answer_text}")
                # 如果JSON解析失败，尝试直接使用文本内容
                return {"status": "success", "answer": answer_text}

        except Exception as e:
            print(f"AI答题失败: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "answer": f"AI调用失败: {str(e)}"}

    def is_available(self):
        """检查AI是否可用"""
        return bool(self.model_name and self.api_key)

    def set_model_config(self, model_name, api_key="", api_base=""):
        """设置模型配置"""
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base
        print(f"模型配置已更新: {model_name}")
        return True

    def is_available(self):
        """检查AI是否可用"""
        return bool(self.model_name)

    def set_model_config(self, model_name, api_key="", api_base=""):
        """设置模型配置"""
        self.model_name = model_name
        self.api_key = api_key
        self.api_base = api_base

        # 更新环境变量
        if api_key:
            os.environ["LITELLM_API_KEY"] = api_key
        if api_base:
            os.environ["LITELLM_API_BASE"] = api_base

        print(f"模型配置已更新: {model_name}")
        return True