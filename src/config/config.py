"""配置管理模块"""
import os
import json
from pathlib import Path


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 配置文件在项目根目录的config文件夹下
        project_root = Path(__file__).parent.parent.parent
        self.config_file = project_root / 'config' / 'config.json'
        self.env_file = project_root / '.env'

        self.default_config = {
            "app": {
                "name": "截图答题工具",
                "version": "1.0.0"
            },
            "hotkey": {
                "modifiers": "alt+shift",
                "key": "q"
            },
            "ai": {
                "model": "deepseek/deepseek-chat",
                "temperature": 0.3,
                "max_tokens": 200
            },
            "ocr": {
                "language": "auto",
                "confidence_threshold": 0.5
            }
        }
        self.config = {}
        self.env_vars = {}
        self.load_config()
        self.load_env_vars()

    def load_config(self):
        """加载JSON配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"配置文件读取失败: {e}，使用默认配置")
                self.config = self.default_config.copy()
                self.save_config()
        else:
            self.config = self.default_config.copy()
            self.save_config()

    def load_env_vars(self):
        """加载环境变量"""
        try:
            from dotenv import load_dotenv
            if self.env_file.exists():
                load_dotenv(self.env_file)
        except ImportError:
            pass

        # 读取环境变量
        self.env_vars = {
            'LITELLM_MODEL': os.getenv('LITELLM_MODEL', ''),
            'LITELLM_API_KEY': os.getenv('LITELLM_API_KEY', ''),
            'LITELLM_API_BASE': os.getenv('LITELLM_API_BASE', '')
        }

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_hotkey_config(self):
        """获取快捷键配置"""
        hotkey_config = self.config.get('hotkey', {})
        return hotkey_config.get('modifiers', 'alt+shift'), hotkey_config.get('key', 'q')

    def update_hotkey_config(self, modifiers, key):
        """更新快捷键配置"""
        if 'hotkey' not in self.config:
            self.config['hotkey'] = {}
        self.config['hotkey']['modifiers'] = modifiers
        self.config['hotkey']['key'] = key
        self.save_config()

    def get_ai_config(self):
        """获取AI配置"""
        ai_config = self.config.get('ai', {})
        return {
            'model': self.env_vars.get('LITELLM_MODEL') or ai_config.get('model', 'deepseek/deepseek-chat'),
            'api_key': self.env_vars.get('LITELLM_API_KEY', ''),
            'api_base': self.env_vars.get('LITELLM_API_BASE', 'https://api.deepseek.com'),
            'temperature': ai_config.get('temperature', 0.3),
            'max_tokens': ai_config.get('max_tokens', 200)
        }

    def get_ocr_config(self):
        """获取OCR配置"""
        return self.config.get('ocr', {
            'language': 'auto',
            'confidence_threshold': 0.5
        })

    def get_app_info(self):
        """获取应用信息"""
        return self.config.get('app', {
            'name': '截图答题工具',
            'version': '1.0.0'
        })
