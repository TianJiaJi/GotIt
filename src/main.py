"""截图答题工具 - 主程序"""
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard, mouse
import os

# 导入各个功能模块
from config.config import ConfigManager
from core.ocr import OCRManager
from core.screenshot import ScreenshotManager
from core.region import RegionManager
from utils.hotkey import HotkeyManager
from ui.ui import HotkeyDialog, OCRResultDialog


class ScreenshotApp:
    """截图答题工具主应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("截图答题工具")
        self.root.geometry("500x600")

        # 设置窗口居中
        self.center_window()

        # 初始化各个功能模块
        self.config_manager = ConfigManager()
        self.ocr_manager = OCRManager()
        self.screenshot_manager = ScreenshotManager()
        self.region_manager = RegionManager()

        # 初始化快捷键管理器
        self.hotkey_manager = HotkeyManager()
        self.setup_hotkey()

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()

        # 创建界面组件
        self.create_widgets()

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
        modifiers, key = self.config_manager.get_hotkey_config()
        hotkey_text = f"当前快捷键: {modifiers.upper().replace('+', ' + ')} + {key.upper()}"

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
            foreground='red'
        )
        self.region_label.pack(pady=5)

        # 区域设置按钮
        region_frame = ttk.Frame(self.root)
        region_frame.pack(pady=5)

        ttk.Button(
            region_frame,
            text="① 设置点1",
            command=self.start_set_point1,
            width=12
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            region_frame,
            text="② 设置点2",
            command=self.start_set_point2,
            width=12
        ).pack(side=tk.LEFT, padx=2)

        # 清除区域按钮
        self.clear_region_button = ttk.Button(
            self.root,
            text="清除区域",
            command=self.clear_capture_region,
            width=15
        )
        self.clear_region_button.pack(pady=5)

        # 测试截图按钮
        test_screenshot_frame = ttk.Frame(self.root)
        test_screenshot_frame.pack(pady=5)

        ttk.Button(
            test_screenshot_frame,
            text="[测试] 区域截图",
            command=self.test_region_screenshot,
            width=20
        ).pack()

        # 使用说明
        help_texts = [
            "提示: 点击按钮后，移动鼠标到目标位置，点击鼠标左键确认",
            "快捷键方式: ALT+CTRL+1/2 直接记录当前鼠标位置",
            "ESC键: 取消设置模式"
        ]

        for help_text in help_texts:
            help_label = ttk.Label(
                self.root,
                text=help_text,
                font=('Arial', 8),
                foreground='darkgray'
            )
            help_label.pack(pady=1)

    def setup_hotkey(self):
        """设置全局快捷键"""
        # 获取当前快捷键配置
        modifiers, key = self.config_manager.get_hotkey_config()
        hotkey_config = {'modifiers': modifiers, 'key': key}

        # 设置快捷键管理器
        self.hotkey_manager.set_hotkey_config(hotkey_config)
        self.hotkey_manager.set_hotkey_callback(self.take_screenshot)
        self.hotkey_manager.set_region_callback(self.handle_region_shortcut)

        # 启动监听器
        self.hotkey_manager.start_listener()

    def handle_region_shortcut(self, digit_value):
        """处理区域设置快捷键"""
        point_num = int(digit_value)
        success, message = self.region_manager.set_point_by_shortcut(point_num)
        if success:
            self.update_region_display()
            self.status_label.config(text=f"[成功] {message}", foreground='green')
        else:
            self.status_label.config(text=f"[错误] {message}", foreground='red')
        self.root.update()

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        # 只在设置模式下处理鼠标左键点击
        if self.region_manager.is_setting_mode() and pressed and button == mouse.Button.left:
            print(f"鼠标左键点击位置: ({x}, {y})")
            # 使用线程安全的方式更新界面
            self.root.after(0, lambda: self.record_position_by_click(x, y))

    def record_position_by_click(self, x, y):
        """通过鼠标点击记录位置"""
        success, message = self.region_manager.record_position_by_click(x, y)
        if success:
            self.update_region_display()
            self.status_label.config(text=f"[成功] {message}", foreground='green')
        else:
            self.status_label.config(text=f"[错误] {message}", foreground='red')
        self.root.update()

    def start_set_point1(self):
        """开始设置第一个区域点"""
        mode, message = self.region_manager.start_set_point1()
        self.status_label.config(text=f"[{mode}] {message}", foreground='blue')
        region_info, color = self.region_manager.get_region_info()
        self.region_label.config(text=f"等待设置点1... (移动鼠标+点击左键)", foreground='blue')
        print(f"进入{mode}，请移动鼠标到目标位置后点击鼠标左键")
        self.root.update()

    def start_set_point2(self):
        """开始设置第二个区域点"""
        mode, message = self.region_manager.start_set_point2()
        self.status_label.config(text=f"[{mode}] {message}", foreground='blue')
        region_info, color = self.region_manager.get_region_info()
        self.region_label.config(text=f"等待设置点2... (移动鼠标+点击左键)", foreground='blue')
        print(f"进入{mode}，请移动鼠标到目标位置后点击鼠标左键")
        self.root.update()

    def clear_capture_region(self):
        """清除截图区域设置"""
        self.region_manager.clear_region()
        self.update_region_display()
        self.status_label.config(text="区域已清除，将截取整个屏幕", foreground='gray')

    def update_region_display(self):
        """更新区域显示"""
        region_info, color = self.region_manager.get_region_info()
        self.region_label.config(text=f"区域: {region_info}", foreground=color)

    def update_hotkey_status(self, text=None):
        """更新快捷键状态显示"""
        if text:
            self.hotkey_status_label.config(text=f"快捷键测试: {text}")
        else:
            key_states = self.hotkey_manager.get_key_states()
            alt_status = "按下" if key_states['alt'] else "释放"
            ctrl_status = "按下" if key_states['ctrl'] else "释放"
            shift_status = "按下" if key_states['shift'] else "释放"
            status_text = f"ALT: {alt_status} | CTRL: {ctrl_status} | SHIFT: {shift_status}"
            self.hotkey_status_label.config(text=f"快捷键测试: {status_text}")

    def test_region_screenshot(self):
        """测试区域截图功能"""
        print("=== 测试区域截图 ===")
        if not self.region_manager.is_region_complete():
            messagebox.showinfo("提示", "请先设置区域点1和点2")
            return

        # 执行截图
        self.take_screenshot()

    def take_screenshot(self):
        """截取屏幕并进行OCR识别"""
        try:
            # 更新状态
            self.status_label.config(text="正在截图...")
            self.root.update()

            # 获取截图区域
            bbox = self.region_manager.get_bbox()

            # 执行截图
            success, filepath, region_text, error = self.screenshot_manager.take_screenshot(bbox)

            if not success:
                self.status_label.config(text=f"[错误] {error}", foreground='red')
                return

            # 更新状态
            self.status_label.config(
                text=f"[成功] 截图已保存，正在OCR识别...",
                foreground='green'
            )
            self.root.update()
            print(f"[成功] 截图已保存: {filepath}")

            # 进行OCR识别
            if self.ocr_manager.is_available():
                ocr_text = self.ocr_manager.recognize_text(filepath)
                if ocr_text:
                    # 保存OCR结果
                    txt_path = self.ocr_manager.save_result(ocr_text, filepath)
                    # 在界面上显示识别结果
                    self.show_ocr_result(ocr_text, filepath, txt_path)
                else:
                    self.status_label.config(text="[成功] 截图完成，OCR未识别到文本", foreground='green')
            else:
                self.status_label.config(text="[成功] 截图完成，OCR不可用", foreground='orange')

        except Exception as e:
            self.status_label.config(
                text=f"[错误] 截图失败: {str(e)}",
                foreground='red'
            )
            print(f"[错误] 截图失败: {str(e)}")

    def show_ocr_result(self, ocr_text, image_path, txt_path=None):
        """显示OCR识别结果"""
        try:
            dialog = OCRResultDialog(self.root, ocr_text, image_path, txt_path)
            # 更新状态
            self.status_label.config(
                text=f"[成功] OCR识别完成",
                foreground='green'
            )
        except Exception as e:
            print(f"显示OCR结果失败: {e}")
            self.status_label.config(
                text=f"[错误] 显示结果失败: {e}",
                foreground='red'
            )

    def open_settings(self):
        """打开设置对话框"""
        current_config = {
            'modifiers': self.hotkey_manager.hotkey_config['modifiers'],
            'key': self.hotkey_manager.hotkey_config['key']
        }
        dialog = HotkeyDialog(self.root, current_config, self.update_hotkey)
        self.root.wait_window(dialog)

    def update_hotkey(self, new_config):
        """更新快捷键配置"""
        # 保存到配置文件
        self.config_manager.update_hotkey_config(
            new_config['modifiers'],
            new_config['key']
        )

        # 更新快捷键管理器配置
        self.hotkey_manager.set_hotkey_config(new_config)

        # 重启键盘监听器
        self.hotkey_manager.restart_listener()

        # 更新界面显示
        modifiers = new_config['modifiers'].upper().replace('+', ' + ')
        key = new_config['key'].upper()
        hotkey_text = f"当前快捷键: {modifiers} + {key}"
        self.hotkey_label.config(text=hotkey_text)

        # 显示确认消息
        messagebox.showinfo("设置成功", f"快捷键已更新为: {modifiers} + {key}")

    def cleanup(self):
        """清理资源"""
        self.hotkey_manager.stop_listener()
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
