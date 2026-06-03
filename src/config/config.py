"""配置管理模块"""
import os
import configparser


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 配置文件在项目根目录的config文件夹下
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_file = os.path.join(project_root, 'config', 'config.ini')
        self.default_config = {
            'hotkey': {
                'modifiers': 'alt+shift',
                'key': 's'
            }
        }
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
        else:
            self.create_default_config()

    def create_default_config(self):
        """创建默认配置文件"""
        for section, options in self.default_config.items():
            self.config.add_section(section)
            for key, value in options.items():
                self.config.set(section, key, value)
        self.save_config()

    def save_config(self):
        """保存配置文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def get_hotkey_config(self):
        """获取快捷键配置"""
        modifiers = self.config.get('hotkey', 'modifiers')
        key = self.config.get('hotkey', 'key')
        return modifiers, key

    def update_hotkey_config(self, modifiers, key):
        """更新快捷键配置"""
        self.config.set('hotkey', 'modifiers', modifiers)
        self.config.set('hotkey', 'key', key)
        self.save_config()
