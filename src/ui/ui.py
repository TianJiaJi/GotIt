"""用户界面模块"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os


class HotkeyDialog(tk.Toplevel):
    """快捷键设置对话框"""

    def __init__(self, parent, current_config, callback):
        super().__init__(parent)
        self.callback = callback
        self.result = None
        self.title("快捷键设置")
        self.geometry("400x300")
        self.make_modal()
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


class OCRResultDialog(tk.Toplevel):
    """OCR结果显示对话框"""

    def __init__(self, parent, ocr_text, image_path, txt_path=None, ai_result=None):
        super().__init__(parent)
        self.title("OCR识别结果")
        self.geometry("600x700")
        self.make_modal()
        self.center_window()
        self.ai_result = ai_result

        # 创建界面
        self.create_widgets(ocr_text, image_path, txt_path)

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

    def create_widgets(self, ocr_text, image_path, txt_path=None):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self,
            text="OCR识别结果",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=10)

        # AI答案显示区域
        if self.ai_result:
            ai_frame = ttk.LabelFrame(self, text="AI 答案", padding=10)
            ai_frame.pack(pady=10, fill=tk.X, padx=10)

            answer_text = self.ai_result.get('answer', '无答案')
            status = self.ai_result.get('status', 'unknown')

            # 根据状态设置颜色
            if status == 'success':
                answer_color = 'green'
                status_text = "✓ 成功"
            elif status == 'error':
                answer_color = 'red'
                status_text = "✗ 错误"
            else:
                answer_color = 'gray'
                status_text = "未知状态"

            # 状态和答案
            ai_info_frame = ttk.Frame(ai_frame)
            ai_info_frame.pack(fill=tk.X)

            ttk.Label(
                ai_info_frame,
                text=f"状态: {status_text}",
                font=('Arial', 9, 'bold')
            ).pack(side=tk.LEFT, padx=5)

            ttk.Label(
                ai_info_frame,
                text=f"答案: {answer_text}",
                font=('Arial', 11, 'bold'),
                foreground=answer_color
            ).pack(side=tk.LEFT, padx=5)

            # 复制答案按钮
            ttk.Button(
                ai_info_frame,
                text="复制答案",
                command=lambda: self.copy_to_clipboard(answer_text),
                width=10
            ).pack(side=tk.RIGHT, padx=5)

        # 图片路径
        path_frame = ttk.Frame(self)
        path_frame.pack(pady=5, fill=tk.X, padx=10)

        ttk.Label(path_frame, text="图片文件:", font=('Arial', 9)).pack(side=tk.LEFT)
        ttk.Label(path_frame, text=os.path.basename(image_path),
                 foreground='blue').pack(side=tk.LEFT, padx=5)

        # 文本文件路径
        if txt_path and os.path.exists(txt_path):
            txt_frame = ttk.Frame(self)
            txt_frame.pack(pady=5, fill=tk.X, padx=10)

            ttk.Label(txt_frame, text="文本文件:", font=('Arial', 9)).pack(side=tk.LEFT)
            ttk.Label(txt_frame, text=os.path.basename(txt_path),
                     foreground='green').pack(side=tk.LEFT, padx=5)

        # OCR结果显示
        result_frame = ttk.Frame(self)
        result_frame.pack(pady=10, fill=tk.BOTH, expand=True, padx=10)

        # 滚动文本框
        text_widget = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            font=('Arial', 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        # 插入OCR结果
        text_widget.insert(tk.END, ocr_text)
        text_widget.config(state=tk.DISABLED)  # 设置为只读

        # 按钮框架
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        # 复制OCR文本按钮
        ttk.Button(
            button_frame,
            text="复制OCR文本",
            command=lambda: self.copy_to_clipboard(ocr_text),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 复制答案按钮（如果有AI结果）
        if self.ai_result and self.ai_result.get('answer'):
            answer_text = self.ai_result.get('answer')
            ttk.Button(
                button_frame,
                text="复制答案",
                command=lambda: self.copy_to_clipboard(answer_text),
                width=12
            ).pack(side=tk.LEFT, padx=5)

        # 关闭按钮
        ttk.Button(
            button_frame,
            text="关闭",
            command=self.destroy,
            width=12
        ).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update()
            messagebox.showinfo("成功", "文本已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")
