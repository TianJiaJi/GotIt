import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageGrab
import datetime
import os
from pynput import keyboard, mouse
import threading
import json
import configparser
from pynput.mouse import Controller as MouseController


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
        self.root.geometry("450x500")

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

        # 初始化区域设置
        self.capture_region = None  # 格式: (x1, y1, x2, y2)
        self.mouse_controller = MouseController()
        self.setting_point_mode = None  # 'point1' 或 'point2'，表示正在设置哪个点

        # 启动鼠标监听器（用于在设置模式下监听鼠标点击）
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()

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
        self.status_label.pack(pady=5)

        # 快捷键状态显示
        self.hotkey_status_label = ttk.Label(
            self.root,
            text="快捷键测试: 按任意键查看检测状态",
            font=('Arial', 9),
            foreground='blue'
        )
        self.hotkey_status_label.pack(pady=2)

        # 区域状态标签
        self.region_label = ttk.Label(
            self.root,
            text="区域: 未设置",
            font=('Arial', 9),
            foreground='gray'
        )
        self.region_label.pack(pady=5)

        # 使用说明
        help_text1 = "区域设置方式1: 按钮点击"
        help_label1 = ttk.Label(
            self.root,
            text=help_text1,
            font=('Arial', 8),
            foreground='darkgray'
        )
        help_label1.pack(pady=1)

        help_text2 = "区域设置方式2: ALT+CTRL+1 设置点1，ALT+CTRL+2 设置点2"
        help_label2 = ttk.Label(
            self.root,
            text=help_text2,
            font=('Arial', 8),
            foreground='darkgray'
        )
        help_label2.pack(pady=1)

        # 清除区域按钮
        self.clear_region_button = ttk.Button(
            self.root,
            text="清除区域",
            command=self.clear_capture_region,
            width=15
        )
        self.clear_region_button.pack(pady=5)

        # 测试区域设置按钮
        test_frame = ttk.Frame(self.root)
        test_frame.pack(pady=5)

        ttk.Button(
            test_frame,
            text="① 设置点1",
            command=self.start_set_point1,
            width=12
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            test_frame,
            text="② 设置点2",
            command=self.start_set_point2,
            width=12
        ).pack(side=tk.LEFT, padx=2)

        # 使用说明
        help_text3 = "提示: 点击按钮后，移动鼠标到目标位置，点击鼠标左键确认"
        help_label3 = ttk.Label(
            self.root,
            text=help_text3,
            font=('Arial', 8),
            foreground='darkgray'
        )
        help_label3.pack(pady=2)

        help_text4 = "快捷键方式: ALT+CTRL+1/2 直接记录当前鼠标位置"
        help_label4 = ttk.Label(
            self.root,
            text=help_text4,
            font=('Arial', 8),
            foreground='darkgray'
        )
        help_label4.pack(pady=1)

        # 测试截图按钮
        test_screenshot_frame = ttk.Frame(self.root)
        test_screenshot_frame.pack(pady=5)

        ttk.Button(
            test_screenshot_frame,
            text="[测试] 区域截图",
            command=self.test_region_screenshot,
            width=20
        ).pack()

    def get_mouse_position(self):
        """获取当前鼠标位置"""
        return self.mouse_controller.position

    def start_set_point1(self):
        """开始设置第一个区域点"""
        self.setting_point_mode = 'point1'
        self.status_label.config(
            text="[设置模式] 移动鼠标到目标位置，点击鼠标左键确认点1",
            foreground='blue'
        )
        self.region_label.config(
            text="等待设置点1... (移动鼠标+点击左键)",
            foreground='blue'
        )
        print("进入设置点1模式，请移动鼠标到目标位置后点击鼠标左键")
        self.root.update()

    def start_set_point2(self):
        """开始设置第二个区域点"""
        self.setting_point_mode = 'point2'
        self.status_label.config(
            text="[设置模式] 移动鼠标到目标位置，点击鼠标左键确认点2",
            foreground='blue'
        )
        self.region_label.config(
            text="等待设置点2... (移动鼠标+点击左键)",
            foreground='blue'
        )
        print("进入设置点2模式，请移动鼠标到目标位置后点击鼠标左键")
        self.root.update()

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        # 只在设置模式下处理鼠标左键点击
        if self.setting_point_mode is not None and pressed and button == mouse.Button.left:
            print(f"鼠标左键点击位置: ({x}, {y})")
            # 使用线程安全的方式更新界面
            self.root.after(0, lambda: self.record_position_by_click(x, y))

    def record_position_by_click(self, x, y):
        """通过鼠标点击记录位置"""
        if self.setting_point_mode is None:
            return

        try:
            if self.setting_point_mode == 'point1':
                print(f"设置点1: 点击位置 ({x}, {y})")
                if self.capture_region is None:
                    self.capture_region = [x, y, None, None]
                else:
                    self.capture_region[0] = x
                    self.capture_region[1] = y

                self.status_label.config(
                    text=f"[成功] 已设置点1: ({x}, {y})",
                    foreground='green'
                )

            elif self.setting_point_mode == 'point2':
                print(f"设置点2: 点击位置 ({x}, {y})")
                if self.capture_region is None:
                    self.capture_region = [None, None, x, y]
                else:
                    self.capture_region[2] = x
                    self.capture_region[3] = y

                self.status_label.config(
                    text=f"[成功] 已设置点2: ({x}, {y})",
                    foreground='green'
                )

            self.setting_point_mode = None
            self.update_region_display()
            self.root.update()

        except Exception as e:
            print(f"设置点失败: {str(e)}")
            self.status_label.config(
                text=f"[错误] 设置失败: {str(e)}",
                foreground='red'
            )

    def cancel_setting_mode(self):
        """取消设置模式"""
        if self.setting_point_mode is not None:
            self.setting_point_mode = None
            self.status_label.config(
                text="[已取消] 设置模式已退出",
                foreground='gray'
            )
            self.update_region_display()
            print("设置模式已取消，可以点击鼠标左键重新开始设置")
            self.root.update()
        """快捷键直接设置点1（用于快捷键触发）"""
        try:
            x, y = self.get_mouse_position()
            print(f"设置点1: 鼠标位置 ({x}, {y})")
            if self.capture_region is None:
                self.capture_region = [x, y, None, None]
            else:
                self.capture_region[0] = x
                self.capture_region[1] = y

            self.update_region_display()
            self.status_label.config(
                text=f"[成功] 已设置点1: ({x}, {y})",
                foreground='green'
            )
            self.root.update()
        except Exception as e:
            print(f"设置点1失败: {str(e)}")

    def set_capture_point2(self):
        """快捷键直接设置点2（用于快捷键触发）"""
        try:
            x, y = self.get_mouse_position()
            print(f"设置点2: 鼠标位置 ({x}, {y})")
            if self.capture_region is None:
                self.capture_region = [None, None, x, y]
            else:
                self.capture_region[2] = x
                self.capture_region[3] = y

            self.update_region_display()
            self.status_label.config(
                text=f"[成功] 已设置点2: ({x}, {y})",
                foreground='green'
            )
            self.root.update()
        except Exception as e:
            print(f"设置点2失败: {str(e)}")

    def clear_capture_region(self):
        """清除截图区域设置"""
        self.capture_region = None
        self.update_region_display()
        self.status_label.config(text="区域已清除，将截取整个屏幕")

    def update_hotkey_status(self, text=None):
        """更新快捷键状态显示"""
        if text:
            self.hotkey_status_label.config(text=f"快捷键测试: {text}")
        else:
            alt_status = "按下" if self.key_states['alt'] else "释放"
            ctrl_status = "按下" if self.key_states['ctrl'] else "释放"
            shift_status = "按下" if self.key_states['shift'] else "释放"
            status_text = f"ALT: {alt_status} | CTRL: {ctrl_status} | SHIFT: {shift_status}"
            self.hotkey_status_label.config(text=f"快捷键测试: {status_text}")

    def update_region_display(self):
        """更新区域显示"""
        if self.capture_region is None:
            self.region_label.config(
                text="区域: 未设置 (请使用下方按钮设置)",
                foreground='red'
            )
        else:
            x1, y1, x2, y2 = self.capture_region
            if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
                # 计算区域的左上角和右下角
                left = min(x1, x2)
                top = min(y1, y2)
                right = max(x1, x2)
                bottom = max(y1, y2)
                width = right - left
                height = bottom - top
                self.region_label.config(
                    text=f"[OK] 区域已设置: ({left}, {top}) 大小: {width}x{height}",
                    foreground='green'
                )
            elif x1 is not None and y1 is not None:
                self.region_label.config(
                    text=f"区域: 点1已设置 ({x1}, {y1})，请设置点2",
                    foreground='orange'
                )
            elif x2 is not None and y2 is not None:
                self.region_label.config(
                    text=f"区域: 点2已设置 ({x2}, {y2})，请设置点1",
                    foreground='orange'
                )
            else:
                self.region_label.config(
                    text="区域: 未设置 (请使用下方按钮设置)",
                    foreground='red'
                )

    def test_region_screenshot(self):
        """测试区域截图功能"""
        print("=== 测试区域截图 ===")
        if self.capture_region is None:
            print("[错误] 区域未设置")
            messagebox.showinfo("提示", "请先设置区域点1和点2")
            return

        x1, y1, x2, y2 = self.capture_region
        if not all(coord is not None for coord in self.capture_region):
            print(f"[错误] 区域设置不完整: 点1({x1}, {y1}), 点2({x2}, {y2})")
            messagebox.showinfo("提示", "请确保两个点都已设置")
            return

        # 执行截图
        self.take_screenshot()

    def take_screenshot(self):
        """截取屏幕并保存"""
        try:
            # 更新状态
            self.status_label.config(text="正在截图...")
            self.root.update()

            # 检查是否设置了截图区域
            if (self.capture_region is not None and
                all(coord is not None for coord in self.capture_region)):
                # 使用指定区域截图
                x1, y1, x2, y2 = self.capture_region
                # 计算区域的左上角和右下角
                bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                screenshot = ImageGrab.grab(bbox=bbox)
                region_text = f"区域 {bbox}"
                print(f"[成功] 使用区域截图: {bbox}")
            else:
                # 截取整个屏幕
                screenshot = ImageGrab.grab()
                region_text = "全屏"
                print("[成功] 使用全屏截图")

            # 生成文件名（使用时间戳）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

            # 保存到项目根目录
            project_root = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(project_root, filename)
            screenshot.save(filepath)

            # 更新状态
            self.status_label.config(
                text=f"[成功] 截图已保存: {filename}",
                foreground='green'
            )
            print(f"[成功] 截图已保存: {filepath}")

        except Exception as e:
            self.status_label.config(
                text=f"[错误] 截图失败: {str(e)}",
                foreground='red'
            )
            print(f"[错误] 截图失败: {str(e)}")

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
            # 减少调试输出，只在重要事件时输出
            # 检查修饰键
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = True
                self.update_hotkey_status()
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = True
                self.update_hotkey_status()
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = True
                self.update_hotkey_status()
            else:
                # 检查普通按键
                char_to_check = None
                try:
                    char = key.char
                    if char:
                        char_to_check = char
                        self.update_hotkey_status(f"按下: {char}")
                except AttributeError:
                    # 处理没有char属性的键，尝试从按键code识别
                    pass

                # 检查ESC键（用于取消设置模式）
                if key == keyboard.Key.esc:
                    print("检测到ESC键")
                    self.cancel_setting_mode()
                    return

                # 检查数字键（包括char为None的情况）
                is_digit_key = False
                digit_value = None

                # 方法1: 检查char属性
                if char_to_check and char_to_check in ['1', '2']:
                    is_digit_key = True
                    digit_value = char_to_check

                # 方法2: 检查按键的vk码（虚拟键码）
                if not is_digit_key and hasattr(key, 'vk'):
                    # 1的vk码是49，2的vk码是50
                    if key.vk == 49:
                        is_digit_key = True
                        digit_value = '1'
                    elif key.vk == 50:
                        is_digit_key = True
                        digit_value = '2'

                if is_digit_key and digit_value:
                    print(f"检测到数字键: {digit_value}, ALT: {self.key_states['alt']}, CTRL: {self.key_states['ctrl']}")
                    status_text = f"数字键: {digit_value} | ALT: {self.key_states['alt']} | CTRL: {self.key_states['ctrl']}"
                    self.update_hotkey_status(status_text)

                    # 如果在设置模式中，提示用户点击鼠标或ESC取消
                    if self.setting_point_mode is not None:
                        print("当前在设置模式中，请点击鼠标左键确认或ESC取消")
                        self.status_label.config(
                            text=f"[提示] 请点击鼠标左键确认当前点，或ESC取消",
                            foreground='orange'
                        )
                        self.root.update()
                        return

                    # 正常的快捷键处理
                    if self.key_states['alt'] and self.key_states['ctrl']:
                        print(f"触发区域设置: 点{digit_value}")
                        if digit_value == '1':
                            self.set_capture_point1()
                        elif digit_value == '2':
                            self.set_capture_point2()
                    else:
                        print(f"修饰键条件不满足，需要ALT+CTRL都按下")

                # 检查截图快捷键
                if char_to_check and char_to_check.lower() == self.hotkey_config['key'].lower():
                    if self.check_hotkey_combination():
                        self.take_screenshot()

        except Exception as e:
            print(f"键盘事件处理错误: {str(e)}")

    def on_key_release(self, key):
        """键盘释放事件处理"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = False
                print("CTRL键释放")
                self.update_hotkey_status()
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = False
                print("ALT键释放")
                self.update_hotkey_status()
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = False
                print("SHIFT键释放")
                self.update_hotkey_status()
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
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
            self.mouse_listener.stop()


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
