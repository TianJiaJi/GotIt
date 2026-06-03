"""用户界面模块"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
from pynput import mouse


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


class RegionDialog(tk.Toplevel):
    """区域设置对话框 - 统一的区域设置界面"""

    def __init__(self, parent, region_manager, callback):
        super().__init__(parent)
        self.callback = callback
        self.region_manager = region_manager
        self.title("区域设置")
        self.geometry("500x400")
        self.make_modal()
        self.center_window()

        # 区域设置状态
        self.setting_mode = None
        self.temp_points = {'point1': None, 'point2': None}

        # 加载当前区域设置
        self.load_current_region()

        # 创建界面
        self.create_widgets()

        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

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

    def load_current_region(self):
        """加载当前区域设置"""
        point1 = self.region_manager.point1
        point2 = self.region_manager.point2
        if point1:
            self.temp_points['point1'] = point1
        if point2:
            self.temp_points['point2'] = point2

    def create_widgets(self):
        """创建界面组件"""
        # 标题和说明
        title_frame = ttk.Frame(self)
        title_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Label(
            title_frame,
            text="🗺️ 设置截图区域",
            font=('Arial', 14, 'bold')
        ).pack()

        ttk.Label(
            title_frame,
            text="设置两个角点来确定答题区域",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=5)

        # 区域显示区域
        display_frame = ttk.LabelFrame(self, text="当前区域", padding=15)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 点1显示
        self.point1_label = ttk.Label(
            display_frame,
            text=f"📍 点1: {self.format_point(self.temp_points['point1'])}",
            font=('Arial', 10)
        )
        self.point1_label.pack(anchor=tk.W, pady=5)

        # 点2显示
        self.point2_label = ttk.Label(
            display_frame,
            text=f"📍 点2: {self.format_point(self.temp_points['point2'])}",
            font=('Arial', 10)
        )
        self.point2_label.pack(anchor=tk.W, pady=5)

        # 区域信息
        self.region_info_label = ttk.Label(
            display_frame,
            text=self.get_region_info(),
            font=('Arial', 9),
            foreground='gray'
        )
        self.region_info_label.pack(anchor=tk.W, pady=5)

        # 操作按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Button(
            button_frame,
            text="设置点1",
            command=lambda: self.start_setting('point1'),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="设置点2",
            command=lambda: self.start_setting('point2'),
            width=12
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="清空",
            command=self.clear_points,
            width=12
        ).pack(side=tk.LEFT, padx=5)

        # 底部按钮
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=15, pady=10)

        ttk.Button(
            bottom_frame,
            text="确定",
            command=self.on_ok,
            width=12
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            bottom_frame,
            text="取消",
            command=self.on_cancel,
            width=12
        ).pack(side=tk.RIGHT, padx=5)

        # 状态提示
        self.status_label = ttk.Label(
            bottom_frame,
            text="点击按钮或使用快捷键设置区域点",
            font=('Arial', 9),
            foreground='blue'
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

    def format_point(self, point):
        """格式化点坐标"""
        if point:
            return f"({point['x']}, {point['y']})"
        return "未设置"

    def get_region_info(self):
        """获取区域信息"""
        p1 = self.temp_points['point1']
        p2 = self.temp_points['point2']

        if p1 and p2:
            width = abs(p2['x'] - p1['x'])
            height = abs(p2['y'] - p1['y'])
            return f"区域大小: {width} × {height} 像素"
        elif p1 or p2:
            return "请设置第二个点完成区域配置"
        else:
            return "请设置两个角点来确定答题区域"

    def start_setting(self, point_name):
        """开始设置点"""
        self.setting_mode = point_name
        self.status_label.config(text=f"正在设置{point_name}，移动鼠标到目标位置后点击...")
        print(f"开始设置{point_name}")

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if pressed and button == mouse.Button.left and self.setting_mode:
            print(f"鼠标点击设置{self.setting_mode}: ({x}, {y})")
            # 记录点位置
            self.temp_points[self.setting_mode] = {'x': x, 'y': y}
            self.after(0, self.update_display_after_click)

    def update_display_after_click(self):
        """点击后更新显示"""
        # 更新点显示
        self.point1_label.config(text=f"📍 点1: {self.format_point(self.temp_points['point1'])}")
        self.point2_label.config(text=f"📍 点2: {self.format_point(self.temp_points['point2'])}")

        # 更新区域信息
        self.region_info_label.config(text=self.get_region_info())

        # 更新状态
        self.setting_mode = None
        self.status_label.config(text="点已记录，请设置下一个点或点击确定", foreground='green')

    def clear_points(self):
        """清空所有点"""
        self.temp_points = {'point1': None, 'point2': None}
        self.update_display_after_click()
        self.status_label.config(text="区域已清空，请重新设置", foreground='orange')

    def on_ok(self):
        """确定按钮"""
        # 检查是否设置了两个点
        if not self.temp_points['point1'] or not self.temp_points['point2']:
            messagebox.showwarning("区域不完整", "请设置两个角点来确定答题区域")
            return

        # 应用区域设置
        self.region_manager.point1 = self.temp_points['point1']
        self.region_manager.point2 = self.temp_points['point2']

        # 调用回调函数
        if self.callback:
            self.callback()

        # 清理资源
        self.cleanup()

        # 关闭对话框
        self.destroy()

    def on_cancel(self):
        """取消按钮"""
        self.cleanup()
        self.destroy()

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive:
            self.mouse_listener.stop()


class SettingsDialog(tk.Toplevel):
    """设置对话框 - 标签页式统一设置界面"""

    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.title("设置")
        self.geometry("600x500")
        self.make_modal()
        self.center_window()

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
        """创建标签页设置界面"""
        # 标题
        title_label = ttk.Label(
            self,
            text="⚙️ 应用设置",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=15)

        # 创建标签页
        notebook = ttk.Notebook(self)
        notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # 基础设置标签页
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="基础设置")
        self.create_basic_settings(basic_frame)

        # AI配置标签页
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="AI配置")
        self.create_ai_settings(ai_frame)

        # OCR配置标签页
        ocr_frame = ttk.Frame(notebook)
        notebook.add(ocr_frame, text="OCR设置")
        self.create_ocr_settings(ocr_frame)

        # 关于标签页
        about_frame = ttk.Frame(notebook)
        notebook.add(about_frame, text="关于")
        self.create_about_tab(about_frame)

        # 底部按钮
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=15, pady=15)

        ttk.Button(
            button_frame,
            text="确定",
            command=self.on_ok,
            width=12
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            button_frame,
            text="取消",
            command=self.destroy,
            width=12
        ).pack(side=tk.RIGHT, padx=5)

    def create_basic_settings(self, parent):
        """创建基础设置页面"""
        # 快捷键配置
        hotkey_frame = ttk.LabelFrame(parent, text="快捷键配置", padding=15)
        hotkey_frame.pack(fill=tk.X, padx=10, pady=10)

        modifiers, key = self.config_manager.get_hotkey_config()

        # 修饰键选择
        mod_frame = ttk.Frame(hotkey_frame)
        mod_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mod_frame, text="修饰键:").pack(side=tk.LEFT)
        self.modifier_var = tk.StringVar(value=modifiers)
        ttk.Combobox(
            mod_frame,
            textvariable=self.modifier_var,
            values=['ctrl', 'alt', 'shift', 'ctrl+alt', 'ctrl+shift', 'alt+shift'],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # 按键选择
        key_frame = ttk.Frame(hotkey_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="按键:").pack(side=tk.LEFT)
        self.key_var = tk.StringVar(value=key)
        ttk.Combobox(
            key_frame,
            textvariable=self.key_var,
            values=['a', 'b', 'c', 'q', 'w', 'e', 'r', 's', '1', '2', '3', '4', '5'],
            state='readonly',
            width=10
        ).pack(side=tk.LEFT, padx=5)

    def create_ai_settings(self, parent):
        """创建AI配置页面"""
        ai_config = self.config_manager.get_ai_config()

        ai_frame = ttk.LabelFrame(parent, text="AI模型配置", padding=15)
        ai_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 模型选择
        model_frame = ttk.Frame(ai_frame)
        model_frame.pack(fill=tk.X, pady=5)
        ttk.Label(model_frame, text="模型:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=ai_config['model'])
        ttk.Entry(
            model_frame,
            textvariable=self.model_var,
            width=30
        ).pack(side=tk.LEFT, padx=5)

        # API密钥
        key_frame = ttk.Frame(ai_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="API密钥:").pack(side=tk.LEFT)
        self.api_key_var = tk.StringVar(value=ai_config['api_key'])
        ttk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            width=40,
            show='*'
        ).pack(side=tk.LEFT, padx=5)

        # API端点
        base_frame = ttk.Frame(ai_frame)
        base_frame.pack(fill=tk.X, pady=5)
        ttk.Label(base_frame, text="API端点:").pack(side=tk.LEFT)
        self.api_base_var = tk.StringVar(value=ai_config['api_base'])
        ttk.Entry(
            base_frame,
            textvariable=self.api_base_var,
            width=40
        ).pack(side=tk.LEFT, padx=5)

        # 高级参数
        advanced_frame = ttk.LabelFrame(ai_frame, text="高级参数", padding=10)
        advanced_frame.pack(fill=tk.X, pady=10)

        # 温度参数
        temp_frame = ttk.Frame(advanced_frame)
        temp_frame.pack(fill=tk.X, pady=5)
        ttk.Label(temp_frame, text="温度:").pack(side=tk.LEFT)
        self.temp_var = tk.StringVar(value=str(ai_config['temperature']))
        ttk.Entry(temp_frame, textvariable=self.temp_var, width=10).pack(side=tk.LEFT, padx=5)

        # 最大tokens
        tokens_frame = ttk.Frame(advanced_frame)
        tokens_frame.pack(fill=tk.X, pady=5)
        ttk.Label(tokens_frame, text="最大Tokens:").pack(side=tk.LEFT)
        self.tokens_var = tk.StringVar(value=str(ai_config['max_tokens']))
        ttk.Entry(tokens_frame, textvariable=self.tokens_var, width=10).pack(side=tk.LEFT, padx=5)

    def create_ocr_settings(self, parent):
        """创建OCR配置页面"""
        ocr_config = self.config_manager.get_ocr_config()

        ocr_frame = ttk.LabelFrame(parent, text="OCR配置", padding=15)
        ocr_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 语言设置
        lang_frame = ttk.Frame(ocr_frame)
        lang_frame.pack(fill=tk.X, pady=5)
        ttk.Label(lang_frame, text="语言:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=ocr_config.get('language', 'auto'))
        ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=['auto', 'zh', 'en', 'zh-en'],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # 置信度阈值
        conf_frame = ttk.Frame(ocr_frame)
        conf_frame.pack(fill=tk.X, pady=5)
        ttk.Label(conf_frame, text="置信度阈值:").pack(side=tk.LEFT)
        self.conf_var = tk.StringVar(value=str(ocr_config.get('confidence_threshold', 0.5)))
        ttk.Entry(conf_frame, textvariable=self.conf_var, width=10).pack(side=tk.LEFT, padx=5)

    def create_about_tab(self, parent):
        """创建关于页面"""
        about_frame = ttk.Frame(parent)
        about_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        app_info = self.config_manager.get_app_info()

        ttk.Label(
            about_frame,
            text=app_info['name'],
            font=('Arial', 16, 'bold')
        ).pack(pady=10)

        ttk.Label(
            about_frame,
            text=f"版本: {app_info['version']}",
            font=('Arial', 10)
        ).pack(pady=5)

        ttk.Label(
            about_frame,
            text="智能截图OCR识别 + AI答题工具",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=5)

        ttk.Label(
            about_frame,
            text="功能特性:",
            font=('Arial', 10, 'bold')
        ).pack(pady=(15, 5))

        features = [
            "📸 区域截图和全屏截图",
            "🔍 高精度OCR识别",
            "🤖 AI智能答题",
            "⌨️ 全局快捷键支持"
        ]

        for feature in features:
            ttk.Label(about_frame, text=feature, font=('Arial', 9)).pack(pady=2)

    def on_ok(self):
        """确定按钮 - 保存配置"""
        try:
            # 保存快捷键配置
            self.config_manager.update_hotkey_config(
                self.modifier_var.get(),
                self.key_var.get()
            )

            # 保存AI配置
            try:
                temp = float(self.temp_var.get())
                tokens = int(self.tokens_var.get())
            except ValueError:
                messagebox.showerror("错误", "参数格式不正确")
                return

            self.config_manager.update_ai_config(
                model=self.model_var.get(),
                api_key=self.api_key_var.get(),
                api_base=self.api_base_var.get()
            )

            messagebox.showinfo("成功", "配置已保存")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
