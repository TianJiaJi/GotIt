"""剪贴板AI对话模块 - 支持上下文保存的剪贴板AI对话"""
import json
import os
from datetime import datetime


class ClipboardChatManager:
    """剪贴板AI对话管理器"""

    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.context_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'clipboard_context.json'
        )

        # 对话上下文
        self.conversation_history = []
        self.max_history = 50  # 最多保存50条对话历史

        # AI配置
        if config_manager:
            ai_config = config_manager.get_ai_config()
            self.model_name = ai_config['model']
            self.api_key = ai_config['api_key']
            self.api_base = ai_config['api_base']
            self.temperature = ai_config.get('temperature', 0.7)
            self.max_tokens = ai_config.get('max_tokens', 2000)
        else:
            self.model_name = os.getenv("LITELLM_MODEL", "deepseek/deepseek-chat")
            self.api_key = os.getenv("LITELLM_API_KEY", "")
            self.api_base = os.getenv("LITELLM_API_BASE", "https://api.deepseek.com")
            self.temperature = 0.7
            self.max_tokens = 2000

        self._initialized = False

        # 加载历史对话
        self._load_context()

    def _get_system_prompt(self):
        """获取系统提示词"""
        return """# Role
你是一个智能对话助手，擅长回答用户的各种问题。

# Guidelines
1. 回答要简洁、准确、有帮助
2. 如果是代码问题，请提供清晰的代码示例
3. 如果是概念解释，请用通俗易懂的语言
4. 保持对话连贯性，参考历史上下文
5. 回答要精炼，适合复制粘贴使用

# Output Format
直接输出回答内容，不要包含任何格式标记或元数据。"""

    def _load_context(self):
        """加载对话上下文"""
        try:
            if os.path.exists(self.context_file):
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('history', [])
                    print(f"已加载 {len(self.conversation_history)} 条对话历史")
        except Exception as e:
            print(f"加载对话历史失败: {e}")
            self.conversation_history = []

    def _save_context(self):
        """保存对话上下文"""
        try:
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'history': self.conversation_history,
                    'last_update': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存对话历史失败: {e}")

    def clear_context(self):
        """清空对话上下文"""
        self.conversation_history = []
        self._save_context()
        return {"status": "success", "message": "对话上下文已清空"}

    def _init_ai(self):
        """初始化AI引擎"""
        if self._initialized:
            return True

        try:
            print(f"剪贴板AI初始化成功，使用模型: {self.model_name}")
            self._initialized = True
            return True
        except Exception as e:
            print(f"剪贴板AI初始化失败: {e}")
            return False

    def process_clipboard_text(self, text):
        """处理剪贴板文本，获取AI回答"""
        if not text or not text.strip():
            return {"status": "error", "message": "剪贴板内容为空"}

        # 初始化AI
        if not self._init_ai():
            return {"status": "error", "message": "AI初始化失败"}

        try:
            # 添加用户消息到历史
            user_message = {"role": "user", "content": text.strip()}
            self.conversation_history.append(user_message)

            # 动态导入litellm
            from litellm import completion

            # 构建消息列表（包含系统提示和历史对话）
            messages = [{"role": "system", "content": self._get_system_prompt()}]
            messages.extend(self.conversation_history[-20:])  # 只保留最近20条

            print(f"发送到AI的对话轮数: {len(self.conversation_history)}")
            print(f"用户输入: {text[:100]}...")

            # 调用AI
            response = completion(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key,
                base_url=self.api_base,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # 提取回答
            assistant_message_content = response.choices[0].message.content.strip()
            print(f"AI回答: {assistant_message_content[:100]}...")

            # 添加助手回答到历史
            assistant_message = {"role": "assistant", "content": assistant_message_content}
            self.conversation_history.append(assistant_message)

            # 限制历史长度
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            # 保存上下文
            self._save_context()

            return {
                "status": "success",
                "answer": assistant_message_content,
                "history_count": len(self.conversation_history)
            }

        except Exception as e:
            print(f"剪贴板AI处理失败: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": f"AI处理失败: {str(e)}"}

    def get_context_info(self):
        """获取上下文信息"""
        return {
            "total_messages": len(self.conversation_history),
            "last_update": datetime.now().isoformat()
        }

    def is_available(self):
        """检查是否可用"""
        return bool(self.model_name and self.api_key)
