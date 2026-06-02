import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
import datetime
import os
from pynput import keyboard
import threading
import json
import configparser


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
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


class HotkeyDialog(tk.Toplevel):
    """快捷键设置对话框"""

    def __init__(self, parent, current_config, callback):
        super().__init__(parent)
        self.callback = callback
        self.result = None
        self.title("快捷键设置")
        self.geometry("400x300")
        self.make_modal()

        # 居中显示
        self.center_window()

        # 当前配置
        self.current_config = current_config

        # 创建界面
        self.create_widgets()

    def make_modal(self):
        """设置为模态对话框"""
        self.transient(self.master)
        self.grab_set()

    def center_window(self):
        """将窗口居中显示"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self,
            text="设置截图快捷键",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=15)

        # 说明文字
        info_label = ttk.Label(
            self,
            text="请选择修饰键和按键组合",
            font=('Arial', 9)
        )
        info_label.pack(pady=5)

        # 修饰键选择
        modifier_frame = ttk.Frame(self)
        modifier_frame.pack(pady=10)

        ttk.Label(modifier_frame, text="修饰键:").pack(side=tk.LEFT, padx=5)

        self.modifier_var = tk.StringVar(value=self.current_config['modifiers'])
        modifier_combobox = ttk.Combobox(
            modifier_frame,
            textvariable=self.modifier_var,
            values=['ctrl', 'alt', 'shift', 'ctrl+alt', 'ctrl+shift', 'alt+shift', 'ctrl+alt+shift'],
            state='readonly',
            width=15
        )
        modifier_combobox.pack(side=tk.LEFT, padx=5)

        # 按键选择
        key_frame = ttk.Frame(self)
        key_frame.pack(pady=10)

        ttk.Label(key_frame, text="按键:").pack(side=tk.LEFT, padx=5)

        self.key_var = tk.StringVar(value=self.current_config['key'])
        key_combobox = ttk.Combobox(
            key_frame,
            textvariable=self.key_var,
            values=['a', 'b', 'c', 's', 'd', 'f', 'q', 'w', 'e', 'r', 'z', 'x', '1', '2', '3', '4', '5'],
            state='readonly',
            width=10
        )
        key_combobox.pack(side=tk.LEFT, padx=5)

        # 当前设置预览
        preview_frame = ttk.Frame(self)
        preview_frame.pack(pady=15)

        ttk.Label(preview_frame, text="当前设置:").pack(side=tk.LEFT, padx=5)

        self.preview_label = ttk.Label(
            preview_frame,
            text=self.get_hotkey_display(),
            font=('Arial', 10, 'bold'),
            foreground='blue'
        )
        self.preview_label.pack(side=tk.LEFT, padx=5)

        # 实时更新预览
        self.modifier_var.trace('w', self.update_preview)
        self.key_var.trace('w', self.update_preview)

        # 按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="确定", command=self.on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.on_cancel, width=10).pack(side=tk.LEFT, padx=5)

    def get_hotkey_display(self):
        """获取快捷键显示文本"""
        modifiers = self.modifier_var.get().upper().replace('+', ' + ')
        key = self.key_var.get().upper()
        return f"{modifiers} + {key}"

    def update_preview(self, *args):
        """更新预览显示"""
        self.preview_label.config(text=self.get_hotkey_display())

    def on_ok(self):
        """确定按钮事件"""
        modifiers = self.modifier_var.get()
        key = self.key_var.get()
        self.result = {'modifiers': modifiers, 'key': key}
        self.callback(self.result)
        self.destroy()

    def on_cancel(self):
        """取消按钮事件"""
        self.destroy()


class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("截图答题工具")
        self.root.geometry("350x250")

        # 设置窗口居中
        self.center_window()

        # 初始化配置管理器
        self.config_manager = ConfigManager()

        # 获取当前快捷键配置
        modifiers, key = self.config_manager.get_hotkey_config()
        self.hotkey_config = {'modifiers': modifiers, 'key': key}

        # 创建界面组件
        self.create_widgets()

        # 初始化快捷键监听
        self.setup_hotkey()

        # 初始化按键状态
        self.key_states = {
            'ctrl': False,
            'alt': False,
            'shift': False
        }

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建界面组件"""
        # 标题标签
        title_label = ttk.Label(
            self.root,
            text="截图答题工具",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=15)

        # 截图按钮
        self.screenshot_button = ttk.Button(
            self.root,
            text="截取屏幕",
            command=self.take_screenshot,
            width=15
        )
        self.screenshot_button.pack(pady=10)

        # 设置按钮
        self.settings_button = ttk.Button(
            self.root,
            text="快捷键设置",
            command=self.open_settings,
            width=15
        )
        self.settings_button.pack(pady=5)

        # 当前快捷键显示
        modifiers = self.hotkey_config['modifiers'].upper().replace('+', ' + ')
        key = self.hotkey_config['key'].upper()
        hotkey_text = f"当前快捷键: {modifiers} + {key}"

        self.hotkey_label = ttk.Label(
            self.root,
            text=hotkey_text,
            font=('Arial', 9),
            foreground='gray'
        )
        self.hotkey_label.pack(pady=10)

        # 状态标签
        self.status_label = ttk.Label(
            self.root,
            text="点击按钮或按快捷键截图",
            font=('Arial', 10)
        )
        self.status_label.pack(pady=10)

    def take_screenshot(self):
        """截取屏幕并保存"""
        try:
            # 更新状态
            self.status_label.config(text="正在截图...")
            self.root.update()

            # 截取整个屏幕
            screenshot = ImageGrab.grab()

            # 生成文件名（使用时间戳）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

            # 保存到项目根目录
            project_root = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(project_root, filename)
            screenshot.save(filepath)

            # 更新状态
            self.status_label.config(text=f"截图已保存: {filename}")
            print(f"截图已保存到: {filepath}")

        except Exception as e:
            self.status_label.config(text=f"截图失败: {str(e)}")
            print(f"截图失败: {str(e)}")

    def open_settings(self):
        """打开设置对话框"""
        dialog = HotkeyDialog(self.root, self.hotkey_config, self.update_hotkey)
        self.root.wait_window(dialog)

    def update_hotkey(self, new_config):
        """更新快捷键配置"""
        # 保存到配置文件
        self.config_manager.update_hotkey_config(
            new_config['modifiers'],
            new_config['key']
        )

        # 更新当前配置
        self.hotkey_config = new_config

        # 重启键盘监听器
        self.restart_listener()

        # 更新界面显示
        modifiers = self.hotkey_config['modifiers'].upper().replace('+', ' + ')
        key = self.hotkey_config['key'].upper()
        hotkey_text = f"当前快捷键: {modifiers} + {key}"
        self.hotkey_label.config(text=hotkey_text)

        # 显示确认消息
        messagebox.showinfo("设置成功", f"快捷键已更新为: {modifiers} + {key}")

    def setup_hotkey(self):
        """设置全局快捷键监听"""
        # 在后台线程中启动键盘监听
        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()

    def restart_listener(self):
        """重启键盘监听器"""
        if hasattr(self, 'listener') and self.listener.is_alive():
            self.listener.stop()
            self.listener.join(timeout=1)

        # 重置按键状态
        for key in self.key_states:
            self.key_states[key] = False

        # 重新启动监听器
        self.setup_hotkey()

    def on_key_press(self, key):
        """键盘按下事件处理"""
        try:
            # 检查修饰键
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = True
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = True
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = True
            else:
                # 检查普通按键
                try:
                    char = key.char
                    if char and char.lower() == self.hotkey_config['key'].lower():
                        if self.check_hotkey_combination():
                            self.take_screenshot()
                except AttributeError:
                    pass

        except Exception as e:
            pass

    def on_key_release(self, key):
        """键盘释放事件处理"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = False
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = False
        except AttributeError:
            pass

    def check_hotkey_combination(self):
        """检查是否满足快捷键组合条件"""
        required_modifiers = self.hotkey_config['modifiers'].lower().split('+')

        for modifier in required_modifiers:
            if not self.key_states.get(modifier, False):
                return False

        return True

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'listener') and self.listener.is_alive():
            self.listener.stop()


def main():
    """主函数"""
    root = tk.Tk()
    app = ScreenshotApp(root)

    # 窗口关闭时清理资源
    def on_closing():
        app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
