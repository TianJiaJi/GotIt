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
from core.ai_answer import AIAnswerManager
from utils.hotkey import HotkeyManager
from ui.ui import HotkeyDialog, OCRResultDialog, RegionDialog, SettingsDialog


class ScreenshotApp:
    """截图答题工具主应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("截图答题工具")
        self.root.geometry("400x500")
        self.root.resizable(False, False)  # 固定窗口大小

        # 设置窗口居中
        self.center_window()

        # 初始化各个功能模块
        self.config_manager = ConfigManager()
        self.ocr_manager = OCRManager()
        self.screenshot_manager = ScreenshotManager()
        self.region_manager = RegionManager()
        self.ai_answer_manager = AIAnswerManager(self.config_manager)

        # 初始化快捷键管理器
        self.hotkey_manager = HotkeyManager()
        self.setup_hotkey()

        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()

        # 操作历史记录
        self.operation_history = []

        # 创建界面组件
        self.create_widgets()

        # 更新系统状态
        self.update_system_status()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建现代化卡片式界面组件"""
        # 标题栏区域 - 包含应用名称和状态指示器
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        title_label = ttk.Label(
            header_frame,
            text="📸 截图答题工具",
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)

        # 系统状态指示器
        self.status_indicator = ttk.Label(
            header_frame,
            text="●",
            font=('Arial', 12),
            foreground='green'
        )
        self.status_indicator.pack(side=tk.RIGHT)

        # 主要操作卡片
        main_card = ttk.LabelFrame(self.root, text="核心操作", padding=15)
        main_card.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 大型截图按钮
        self.screenshot_button = ttk.Button(
            main_card,
            text="📷 截图答题",
            command=self.take_screenshot,
            width=25,
            style='Accent.TButton'  # 使用强调样式
        )
        self.screenshot_button.pack(pady=15)

        # 快捷键和区域状态显示
        info_frame = ttk.Frame(main_card)
        info_frame.pack(fill=tk.X, pady=10)

        # 快捷键信息
        modifiers, key = self.config_manager.get_hotkey_config()
        hotkey_text = f"⌨️  快捷键: {modifiers.upper().replace('+', ' + ')} + {key.upper()}"
        self.hotkey_label = ttk.Label(
            info_frame,
            text=hotkey_text,
            font=('Arial', 10),
            foreground='#555'
        )
        self.hotkey_label.pack(anchor=tk.W, pady=2)

        # 区域状态信息
        self.region_label = ttk.Label(
            info_frame,
            text="📏 区域: 未设置",
            font=('Arial', 10),
            foreground='#d32f2f'
        )
        self.region_label.pack(anchor=tk.W, pady=2)

        # 当前状态显示
        self.status_label = ttk.Label(
            main_card,
            text="✅ 系统就绪，可以开始使用",
            font=('Arial', 9),
            foreground='#2e7d32'
        )
        self.status_label.pack(pady=10)

        # 功能按钮组
        button_frame = ttk.Frame(main_card)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            button_frame,
            text="⚙️ 设置",
            command=self.open_settings,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🗺️ 区域",
            command=self.open_region_settings,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📖 帮助",
            command=self.show_help,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 底部状态栏
        status_bar = ttk.Frame(self.root)
        status_bar.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(
            status_bar,
            text="💡 提示: 使用快捷键或点击按钮开始截图答题",
            font=('Arial', 8),
            foreground='#666'
        ).pack(side=tk.LEFT)

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
        # 更新区域标签，使用新的图标样式
        if "未设置" in region_info:
            self.region_label.config(text=f"📏 {region_info}", foreground='#d32f2f')
        elif "部分设置" in region_info:
            self.region_label.config(text=f"📏 {region_info}", foreground='#f9a825')
        else:
            self.region_label.config(text=f"📏 {region_info}", foreground='#2e7d32')

        # 更新系统状态
        self.update_system_status()

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

                    # 调用AI进行答题
                    self.status_label.config(
                        text=f"[成功] OCR识别完成，正在AI答题...",
                        foreground='blue'
                    )
                    self.root.update()

                    ai_result = self.ai_answer_manager.get_answer(ocr_text)

                    # 在界面上显示识别结果和AI答案
                    self.show_ocr_result(ocr_text, filepath, txt_path, ai_result)
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

    def show_ocr_result(self, ocr_text, image_path, txt_path=None, ai_result=None):
        """显示OCR识别结果"""
        try:
            dialog = OCRResultDialog(self.root, ocr_text, image_path, txt_path, ai_result)
            # 更新状态
            if ai_result and ai_result.get('status') == 'success':
                self.status_label.config(
                    text=f"[成功] AI答题完成: {ai_result.get('answer', '无答案')}",
                    foreground='green'
                )
            else:
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
        try:
            from ui.ui import SettingsDialog
            dialog = SettingsDialog(self.root, self.config_manager)
            self.root.wait_window(dialog)
            # 更新界面显示
            self.update_display_after_settings()
        except ImportError:
            # 如果SettingsDialog还未实现，使用原来的快捷键设置
            self.open_hotkey_settings()

    def open_hotkey_settings(self):
        """打开快捷键设置对话框（兼容方法）"""
        current_config = {
            'modifiers': self.hotkey_manager.hotkey_config['modifiers'],
            'key': self.hotkey_manager.hotkey_config['key']
        }
        dialog = HotkeyDialog(self.root, current_config, self.update_hotkey)
        self.root.wait_window(dialog)

    def open_region_settings(self):
        """打开区域设置对话框"""
        try:
            from ui.ui import RegionDialog
            dialog = RegionDialog(self.root, self.region_manager, self.update_region_display)
            self.root.wait_window(dialog)
        except ImportError:
            # 如果RegionDialog还未实现，显示提示
            messagebox.showinfo("区域设置", "区域设置功能正在开发中，请使用快捷键：\nALT+CTRL+1 设置点1\nALT+CTRL+2 设置点2")

    def show_help(self):
        """显示帮助信息"""
        help_text = """📸 截图答题工具使用指南

🚀 快速开始：
1. 点击"截图答题"按钮或使用快捷键
2. 程序会自动截图并识别题目
3. AI会直接给出答案

⌨️ 快捷键：
• ALT+SHIFT+Q：截图答题
• ALT+CTRL+1：设置截图区域点1
• ALT+CTRL+2：设置截图区域点2

📋 功能说明：
• 区域设置：固定答题区域，提高效率
• 配置管理：自定义AI模型、参数等
• 状态指示：绿色=正常，红色=需配置

💡 提示：
首次使用建议先配置区域，然后就可以一键答题了！"""
        messagebox.showinfo("使用帮助", help_text)

    def update_display_after_settings(self):
        """设置后更新界面显示"""
        # 更新快捷键显示
        modifiers, key = self.config_manager.get_hotkey_config()
        hotkey_text = f"⌨️  快捷键: {modifiers.upper().replace('+', ' + ')} + {key.upper()}"
        self.hotkey_label.config(text=hotkey_text)

        # 更新区域显示
        self.update_region_display()

        # 更新系统状态
        self.update_system_status()

    def update_system_status(self):
        """更新系统状态指示器"""
        # 检查系统状态
        region_complete = self.region_manager.is_region_complete()
        ai_available = self.ai_answer_manager.is_available()
        ocr_available = self.ocr_manager.is_available()

        if region_complete and ai_available and ocr_available:
            self.status_indicator.config(text="●", foreground='green')
            self.status_label.config(text="✅ 系统就绪，可以开始使用", foreground='#2e7d32')
        elif ai_available and ocr_available:
            self.status_indicator.config(text="●", foreground='#f9a825')  # 黄色
            self.status_label.config(text="⚠️ 建议设置答题区域以获得更好体验", foreground='#f9a825')
        else:
            self.status_indicator.config(text="●", foreground='red')
            self.status_label.config(text="❌ 请先配置API密钥", foreground='red')

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
        hotkey_text = f"⌨️  快捷键: {modifiers} + {key}"
        self.hotkey_label.config(text=hotkey_text)

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
