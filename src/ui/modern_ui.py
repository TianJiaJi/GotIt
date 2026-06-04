"""现代化扁平风格UI模块"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
from pynput import mouse


class ModernTheme:
    """现代化设计主题"""

    # 颜色系统 - Windows 11 风格
    PRIMARY = "#5B5FC7"      # 主色调 - 现代蓝紫
    PRIMARY_LIGHT = "#858BD8"  # 浅主色
    PRIMARY_DARK = "#3F45A5"   # 深主色

    BACKGROUND = "#F9F9F9"    # 背景色
    SURFACE = "#FFFFFF"       # 表面色
    SURFACE_VARIANT = "#F0F0F0"  # 表面变体
    BUTTON_SECONDARY = "#E8E8E8"  # 次要按钮背景色 - 浅灰色

    TEXT_PRIMARY = "#1A1A1A"  # 主要文字
    TEXT_SECONDARY = "#666666"  # 次要文字
    TEXT_HINT = "#999999"      # 提示文字

    SUCCESS = "#00C853"       # 成功色
    WARNING = "#FF9800"       # 警告色
    ERROR = "#F44336"         # 错误色
    INFO = "#2196F3"          # 信息色

    BORDER = "#E0E0E0"        # 边框色
    BORDER_LIGHT = "#F5F5F5"  # 浅边框

    SHADOW = "rgba(0, 0, 0, 0.1)"  # 阴影

    # 尺寸规范
    BORDER_RADIUS = 8         # 圆角半径
    PADDING_SMALL = 8         # 小间距
    PADDING_MEDIUM = 16       # 中间距
    PADDING_LARGE = 24        # 大间距

    # 字体大小
    FONT_SIZE_H1 = 24         # 一级标题
    FONT_SIZE_H2 = 18         # 二级标题
    FONT_SIZE_H3 = 16         # 三级标题
    FONT_SIZE_BODY = 14       # 正文
    FONT_SIZE_CAPTION = 12    # 说明文字


class ModernButton(tk.Canvas):
    """现代化按钮组件"""

    def __init__(self, parent, text, command=None, icon=None,
                 style="primary", size="medium", **kwargs):
        self.command = command
        self.text = text
        self.icon = icon
        self.style = style  # 保存样式信息
        self.is_hovered = False
        self.is_pressed = False

        # 根据样式设置颜色
        self.style_config = self._get_style_config(style)
        self.size_config = self._get_size_config(size)

        # 提取自定义参数
        width_extra = kwargs.pop('width_extra', 0)

        # 设置画布大小
        width = self.size_config['width'] + width_extra
        height = self.size_config['height']

        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, **kwargs)

        self._draw_button()
        self._bind_events()

    def _get_style_config(self, style):
        """获取样式配置"""
        configs = {
            "primary": {
                "bg": ModernTheme.PRIMARY,
                "hover": ModernTheme.PRIMARY_LIGHT,
                "text": "white",
                "disabled": "#CCCCCC"
            },
            "secondary": {
                "bg": ModernTheme.BUTTON_SECONDARY,
                "hover": ModernTheme.SURFACE_VARIANT,
                "text": ModernTheme.TEXT_PRIMARY,
                "disabled": "#F5F5F5"
            },
            "success": {
                "bg": ModernTheme.SUCCESS,
                "hover": "#00E676",
                "text": "white",
                "disabled": "#CCCCCC"
            },
            "danger": {
                "bg": ModernTheme.ERROR,
                "hover": "#FF5252",
                "text": "white",
                "disabled": "#CCCCCC"
            }
        }
        return configs.get(style, configs["primary"])

    def _get_size_config(self, size):
        """获取尺寸配置"""
        configs = {
            "small": {"width": 80, "height": 32, "font_size": 11},
            "medium": {"width": 120, "height": 40, "font_size": 13},
            "large": {"width": 180, "height": 48, "font_size": 15}
        }
        return configs.get(size, configs["medium"])

    def _draw_button(self):
        """绘制按钮"""
        self.delete("all")

        # 确定当前颜色
        if self.is_pressed:
            bg_color = self.style_config["hover"]
        elif self.is_hovered:
            bg_color = self.style_config["hover"]
        else:
            bg_color = self.style_config["bg"]

        # 绘制圆角矩形
        width = int(self['width'])
        height = int(self['height'])
        r = ModernTheme.BORDER_RADIUS

        # 简化版本：使用普通矩形，添加边框使其可见
        outline_color = ModernTheme.BORDER if self.style == "secondary" else ""
        self.create_rectangle(0, 0, width, height, fill=bg_color, outline=outline_color)

        # 绘制文字和图标
        text_color = self.style_config["text"]
        font_size = self.size_config["font_size"]

        if self.icon:
            text = f"{self.icon} {self.text}"
        else:
            text = self.text

        self.create_text(width//2, height//2, text=text,
                        fill=text_color, font=('Arial', font_size, 'bold'))

    def _bind_events(self):
        """绑定事件"""
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_press)
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_enter(self, event):
        """鼠标进入"""
        self.is_hovered = True
        self._draw_button()

    def _on_leave(self, event):
        """鼠标离开"""
        self.is_hovered = False
        self._draw_button()

    def _on_press(self, event):
        """鼠标按下"""
        self.is_pressed = True
        self._draw_button()

    def _on_release(self, event):
        """鼠标释放"""
        self.is_pressed = False
        self._draw_button()
        if self.command:
            self.command()


class ModernCard(tk.Frame):
    """现代化卡片组件"""

    def __init__(self, parent, title=None, padding=ModernTheme.PADDING_MEDIUM, **kwargs):
        super().__init__(parent, bg=ModernTheme.SURFACE,
                        highlightbackground=ModernTheme.BORDER,
                        highlightthickness=1, **kwargs)

        self.padding = padding
        self.title_widget = None

        # 内容器器（总是创建）
        self.content_frame = tk.Frame(self, bg=ModernTheme.SURFACE)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=padding, pady=padding)

        if title:
            self._add_title(title)

    def _add_title(self, title):
        """添加标题"""
        title_frame = tk.Frame(self.content_frame, bg=ModernTheme.SURFACE)
        title_frame.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_MEDIUM))

        self.title_widget = tk.Label(
            title_frame,
            text=title,
            font=('Arial', ModernTheme.FONT_SIZE_H3, 'bold'),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        )
        self.title_widget.pack(side=tk.LEFT)

    def add_content(self, widget, **pack_options):
        """添加内容组件"""
        default_options = {'fill': tk.BOTH, 'expand': True}
        default_options.update(pack_options)
        widget.pack(in_=self.content_frame, **default_options)
        return widget


class ModernStatusBar(tk.Frame):
    """现代化状态栏"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=ModernTheme.SURFACE_VARIANT,
                        highlightbackground=ModernTheme.BORDER,
                        highlightthickness=1, **kwargs)

        self._create_widgets()

    def _create_widgets(self):
        """创建组件"""
        # 状态指示器
        self.status_indicator = tk.Label(
            self,
            text="●",
            font=('Arial', 12),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.SUCCESS
        )
        self.status_indicator.pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

        # 状态文本
        self.status_text = tk.Label(
            self,
            text="系统就绪",
            font=('Arial', ModernTheme.FONT_SIZE_CAPTION),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.TEXT_SECONDARY
        )
        self.status_text.pack(side=tk.LEFT, padx=ModernTheme.PADDING_SMALL)

        # 右侧信息
        self.info_label = tk.Label(
            self,
            text="",
            font=('Arial', ModernTheme.FONT_SIZE_CAPTION),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.TEXT_HINT
        )
        self.info_label.pack(side=tk.RIGHT, padx=ModernTheme.PADDING_MEDIUM)

    def set_status(self, text, status_type="info"):
        """设置状态"""
        self.status_text.config(text=text)

        colors = {
            "success": ModernTheme.SUCCESS,
            "warning": ModernTheme.WARNING,
            "error": ModernTheme.ERROR,
            "info": ModernTheme.INFO
        }
        color = colors.get(status_type, ModernTheme.INFO)
        self.status_indicator.config(fg=color)

    def set_info(self, text):
        """设置右侧信息"""
        self.info_label.config(text=text)


class ModernResultDialog(tk.Toplevel):
    """现代化结果显示对话框"""

    def __init__(self, parent, ocr_text, image_path, ai_result=None):
        super().__init__(parent)
        self.title("识别结果")
        self.geometry("700x600")
        self.ai_result = ai_result
        self.ocr_text = ocr_text
        self.image_path = image_path

        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        """设置窗口"""
        self.transient(self.master)
        self.grab_set()
        self.config(bg=ModernTheme.BACKGROUND)

        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_container = tk.Frame(self, bg=ModernTheme.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LARGE,
                           pady=ModernTheme.PADDING_LARGE)

        # AI答案卡片
        if self.ai_result:
            self._create_ai_answer_card(main_container)

        # OCR结果卡片
        self._create_ocr_result_card(main_container)

        # 按钮区域
        self._create_button_area(main_container)

    def _create_ai_answer_card(self, parent):
        """创建AI答案卡片"""
        card = ModernCard(parent, title="🤖 AI答案",
                         padding=ModernTheme.PADDING_MEDIUM)
        card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_MEDIUM))

        answer_text = self.ai_result.get('answer', '无答案')
        status = self.ai_result.get('status', 'unknown')

        # 状态和答案
        content_frame = tk.Frame(card.content_frame, bg=ModernTheme.SURFACE)
        content_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        # 状态标签
        status_colors = {
            "success": ModernTheme.SUCCESS,
            "error": ModernTheme.ERROR,
            "unknown": ModernTheme.TEXT_HINT
        }
        status_texts = {
            "success": "✓ 成功",
            "error": "✗ 错误",
            "unknown": "未知"
        }

        status_color = status_colors.get(status, ModernTheme.TEXT_HINT)
        status_text = status_texts.get(status, "未知")

        tk.Label(
            content_frame,
            text=f"状态: {status_text}",
            font=('Arial', ModernTheme.FONT_SIZE_BODY, 'bold'),
            bg=ModernTheme.SURFACE,
            fg=status_color
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_SMALL)

        # 答案显示
        tk.Label(
            content_frame,
            text=f"答案: {answer_text}",
            font=('Arial', ModernTheme.FONT_SIZE_H3, 'bold'),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.PRIMARY
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

        # 复制按钮
        copy_btn = ModernButton(
            content_frame,
            text="复制答案",
            command=lambda: self._copy_to_clipboard(answer_text),
            style="secondary",
            size="small",
            width_extra=80
        )
        copy_btn.pack(side=tk.RIGHT, padx=ModernTheme.PADDING_SMALL)

    def _create_ocr_result_card(self, parent):
        """创建OCR结果卡片"""
        card = ModernCard(parent, title="📝 OCR识别结果",
                         padding=ModernTheme.PADDING_MEDIUM)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, ModernTheme.PADDING_MEDIUM))

        # 文本显示区域
        text_frame = tk.Frame(card.content_frame, bg=ModernTheme.SURFACE_VARIANT)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # 滚动文本
        text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
            selectbackground=ModernTheme.PRIMARY_LIGHT,
            selectforeground="white",
            relief=tk.FLAT,
            padx=ModernTheme.PADDING_MEDIUM,
            pady=ModernTheme.PADDING_MEDIUM
        )
        text_widget.pack(fill=tk.BOTH, expand=True)

        # 插入文本
        text_widget.insert(tk.END, self.ocr_text)
        text_widget.config(state=tk.DISABLED)

    def _create_button_area(self, parent):
        """创建按钮区域"""
        button_frame = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        button_frame.pack(fill=tk.X, pady=(ModernTheme.PADDING_MEDIUM, 0))

        # 复制OCR文本
        copy_ocr_btn = ModernButton(
            button_frame,
            text="📋 复制OCR文本",
            command=lambda: self._copy_to_clipboard(self.ocr_text),
            style="secondary",
            size="medium"
        )
        copy_ocr_btn.pack(side=tk.LEFT, padx=ModernTheme.PADDING_SMALL)

        # 关闭按钮
        close_btn = ModernButton(
            button_frame,
            text="✓ 关闭",
            command=self.destroy,
            style="primary",
            size="medium"
        )
        close_btn.pack(side=tk.RIGHT, padx=ModernTheme.PADDING_SMALL)

    def _copy_to_clipboard(self, text):
        """复制到剪贴板"""
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("成功", "文本已复制到剪贴板")
        except Exception as e:
            messagebox.showerror("错误", f"复制失败: {e}")


class ModernRegionDialog(tk.Toplevel):
    """现代化区域设置对话框 - 保留所有快捷键功能"""

    def __init__(self, parent, region_manager, callback):
        super().__init__(parent)
        self.region_manager = region_manager
        self.callback = callback
        self.title("区域设置")
        self.geometry("600x700")  # 增加窗口高度到700像素

        self.setting_mode = None
        self.temp_points = {'point1': None, 'point2': None}

        # 设置窗口属性
        self._setup_window()

        # 加载当前区域设置
        self._load_current_region()

        # 创建界面组件
        self._create_widgets()

        # 在创建完组件后居中窗口
        self._center_window()

        # 启动鼠标监听（最后启动，避免影响布局）
        self._start_mouse_listener()

    def _setup_window(self):
        """设置窗口"""
        self.transient(self.master)
        self.grab_set()
        self.config(bg=ModernTheme.BACKGROUND)

    def _center_window(self):
        """居中显示窗口"""
        # 先强制更新布局
        self.update()

        # 获取实际尺寸
        width = self.winfo_width()
        height = self.winfo_height()

        # 如果尺寸太小，使用预设尺寸
        if width < 100 or height < 100:
            width = 600
            height = 700

        # 计算居中位置
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _load_current_region(self):
        """加载当前区域"""
        if self.region_manager.point1:
            self.temp_points['point1'] = self.region_manager.point1
        if self.region_manager.point2:
            self.temp_points['point2'] = self.region_manager.point2

    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_container = tk.Frame(self, bg=ModernTheme.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LARGE,
                           pady=ModernTheme.PADDING_LARGE)

        # 标题卡片
        self._create_title_card(main_container)

        # 区域显示卡片
        self._create_region_display_card(main_container)

        # 快捷键提示卡片
        self._create_shortcut_info_card(main_container)

        # 操作按钮
        self._create_action_buttons(main_container)

        # 状态标签 - 放在按钮下方
        self.status_label = tk.Label(
            main_container,
            text="点击按钮或使用快捷键设置区域点",
            font=('Arial', ModernTheme.FONT_SIZE_CAPTION),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.INFO
        )
        self.status_label.pack(pady=(ModernTheme.PADDING_MEDIUM, 0))

    def _create_title_card(self, parent):
        """创建标题卡片"""
        card = ModernCard(parent, padding=ModernTheme.PADDING_MEDIUM)
        card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        # 标题
        tk.Label(
            card.content_frame,
            text="🗺️ 设置截图区域",
            font=('Arial', ModernTheme.FONT_SIZE_H1, 'bold'),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(pady=(0, ModernTheme.PADDING_SMALL))

        # 说明
        tk.Label(
            card.content_frame,
            text="设置两个角点来确定答题区域 - 支持快捷键和鼠标点击",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY
        ).pack()

    def _create_region_display_card(self, parent):
        """创建区域显示卡片"""
        self.region_card = ModernCard(parent, title="📍 当前区域",
                                      padding=ModernTheme.PADDING_SMALL)
        self.region_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        # 点1显示
        self.point1_label = tk.Label(
            self.region_card.content_frame,
            text=f"点1: {self._format_point(self.temp_points['point1'])}",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        )
        self.point1_label.pack(anchor=tk.W, pady=ModernTheme.PADDING_SMALL)

        # 点2显示
        self.point2_label = tk.Label(
            self.region_card.content_frame,
            text=f"点2: {self._format_point(self.temp_points['point2'])}",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        )
        self.point2_label.pack(anchor=tk.W, pady=ModernTheme.PADDING_SMALL)

        # 区域信息
        self.region_info_label = tk.Label(
            self.region_card.content_frame,
            text=self._get_region_info(),
            font=('Arial', ModernTheme.FONT_SIZE_CAPTION),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_HINT
        )
        self.region_info_label.pack(anchor=tk.W, pady=ModernTheme.PADDING_SMALL)

    def _create_shortcut_info_card(self, parent):
        """创建快捷键提示卡片"""
        card = ModernCard(parent, title="⌨️ 快捷键操作",
                         padding=ModernTheme.PADDING_SMALL)
        card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        shortcuts = [
            ("ALT + CTRL + 1", "设置区域点1（当前鼠标位置）"),
            ("ALT + CTRL + 2", "设置区域点2（当前鼠标位置）"),
            ("ESC", "取消设置模式")
        ]

        for shortcut, description in shortcuts:
            row = tk.Frame(card.content_frame, bg=ModernTheme.SURFACE)
            row.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

            # 快捷键
            tk.Label(
                row,
                text=shortcut,
                font=('Arial', ModernTheme.FONT_SIZE_BODY, 'bold'),
                bg=ModernTheme.SURFACE_VARIANT,
                fg=ModernTheme.PRIMARY,
                padx=ModernTheme.PADDING_SMALL,
                pady=2
            ).pack(side=tk.LEFT, padx=(0, ModernTheme.PADDING_MEDIUM))

            # 说明
            tk.Label(
                row,
                text=description,
                font=('Arial', ModernTheme.FONT_SIZE_BODY),
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.TEXT_SECONDARY
            ).pack(side=tk.LEFT)

    def _create_action_buttons(self, parent):
        """创建操作按钮 - 使用简单布局避免压缩"""
        button_frame = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        button_frame.pack(fill=tk.X, pady=(ModernTheme.PADDING_MEDIUM, 0))

        # 第一行按钮：设置点1、设置点2、清空
        row1_frame = tk.Frame(button_frame, bg=ModernTheme.BACKGROUND)
        row1_frame.pack(fill=tk.X, pady=(0, 4))

        ModernButton(
            row1_frame,
            text="设置点1",
            icon="📍",
            command=lambda: self._start_setting('point1'),
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=4)

        ModernButton(
            row1_frame,
            text="设置点2",
            icon="📍",
            command=lambda: self._start_setting('point2'),
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=4)

        ModernButton(
            row1_frame,
            text="清空",
            icon="🗑️",
            command=self._clear_points,
            style="danger",
            size="medium"
        ).pack(side=tk.LEFT, padx=4)

        # 第二行按钮：确定、取消（右对齐）
        row2_frame = tk.Frame(button_frame, bg=ModernTheme.BACKGROUND)
        row2_frame.pack(fill=tk.X)

        # 添加一个可扩展的spacer
        spacer = tk.Frame(row2_frame, bg=ModernTheme.BACKGROUND)
        spacer.pack(side=tk.LEFT, expand=True, fill=tk.X)

        ModernButton(
            row2_frame,
            text="确定",
            icon="✓",
            command=self._on_ok,
            style="primary",
            size="medium"
        ).pack(side=tk.RIGHT, padx=4)

        ModernButton(
            row2_frame,
            text="取消",
            command=self._on_cancel,
            style="secondary",
            size="medium"
        ).pack(side=tk.RIGHT, padx=4)

    def _start_setting(self, point_name):
        """开始设置点"""
        self.setting_mode = point_name
        self.status_label.config(
            text=f"正在设置{point_name}，移动鼠标到目标位置后点击...",
            fg=ModernTheme.INFO
        )

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if pressed and button == mouse.Button.left and self.setting_mode:
            self.temp_points[self.setting_mode] = {'x': x, 'y': y}
            self.after(0, self._update_display_after_click)

    def _update_display_after_click(self):
        """点击后更新显示"""
        # 更新点显示
        self.point1_label.config(
            text=f"点1: {self._format_point(self.temp_points['point1'])}"
        )
        self.point2_label.config(
            text=f"点2: {self._format_point(self.temp_points['point2'])}"
        )

        # 更新区域信息
        self.region_info_label.config(text=self._get_region_info())

        # 更新状态
        self.setting_mode = None
        self.status_label.config(
            text="点已记录，请设置下一个点或点击确定",
            fg=ModernTheme.SUCCESS
        )

    def _clear_points(self):
        """清空所有点"""
        self.temp_points = {'point1': None, 'point2': None}
        self._update_display_after_click()
        self.status_label.config(
            text="区域已清空，请重新设置",
            fg=ModernTheme.WARNING
        )

    def _format_point(self, point):
        """格式化点坐标"""
        if point:
            return f"({point['x']}, {point['y']})"
        return "未设置"

    def _get_region_info(self):
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

    def _start_mouse_listener(self):
        """启动鼠标监听"""
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.mouse_listener.start()

    def _on_ok(self):
        """确定按钮"""
        if not self.temp_points['point1'] or not self.temp_points['point2']:
            messagebox.showwarning("区域不完整", "请设置两个角点来确定答题区域")
            return

        # 应用区域设置
        self.region_manager.point1 = self.temp_points['point1']
        self.region_manager.point2 = self.temp_points['point2']

        if self.callback:
            self.callback()

        self._cleanup()
        self.destroy()

    def _on_cancel(self):
        """取消按钮"""
        self._cleanup()
        self.destroy()

    def _cleanup(self):
        """清理资源"""
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive:
            self.mouse_listener.stop()


class ModernSettingsDialog(tk.Toplevel):
    """现代化设置对话框"""

    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.title("设置")
        self.geometry("700x600")

        self._setup_window()
        self._create_widgets()

    def _setup_window(self):
        """设置窗口"""
        self.transient(self.master)
        self.grab_set()
        self.config(bg=ModernTheme.BACKGROUND)

        # 居中显示
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def _create_widgets(self):
        """创建组件"""
        # 主容器
        main_container = tk.Frame(self, bg=ModernTheme.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LARGE,
                           pady=ModernTheme.PADDING_LARGE)

        # 标题
        tk.Label(
            main_container,
            text="⚙️ 应用设置",
            font=('Arial', ModernTheme.FONT_SIZE_H1, 'bold'),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(pady=(0, ModernTheme.PADDING_LARGE))

        # 创建标签页
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # 基础设置标签页
        basic_frame = tk.Frame(notebook, bg=ModernTheme.BACKGROUND)
        notebook.add(basic_frame, text="基础设置")
        self._create_basic_settings(basic_frame)

        # AI配置标签页
        ai_frame = tk.Frame(notebook, bg=ModernTheme.BACKGROUND)
        notebook.add(ai_frame, text="AI配置")
        self._create_ai_settings(ai_frame)

        # OCR配置标签页
        ocr_frame = tk.Frame(notebook, bg=ModernTheme.BACKGROUND)
        notebook.add(ocr_frame, text="OCR设置")
        self._create_ocr_settings(ocr_frame)

        # 通知配置标签页
        notification_frame = tk.Frame(notebook, bg=ModernTheme.BACKGROUND)
        notebook.add(notification_frame, text="通知设置")
        self._create_notification_settings(notification_frame)

        # 关于标签页
        about_frame = tk.Frame(notebook, bg=ModernTheme.BACKGROUND)
        notebook.add(about_frame, text="关于")
        self._create_about_tab(about_frame)

        # 底部按钮
        button_frame = tk.Frame(main_container, bg=ModernTheme.BACKGROUND)
        button_frame.pack(fill=tk.X, pady=(ModernTheme.PADDING_LARGE, 0))

        ModernButton(
            button_frame,
            text="确定",
            icon="✓",
            command=self._on_ok,
            style="primary",
            size="medium"
        ).pack(side=tk.RIGHT, padx=ModernTheme.PADDING_SMALL)

        ModernButton(
            button_frame,
            text="取消",
            command=self.destroy,
            style="secondary",
            size="medium"
        ).pack(side=tk.RIGHT, padx=ModernTheme.PADDING_SMALL)

    def _create_basic_settings(self, parent):
        """创建基础设置页面"""
        container = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_MEDIUM,
                      pady=ModernTheme.PADDING_MEDIUM)

        # 快捷键配置卡片
        hotkey_card = ModernCard(container, title="⌨️ 快捷键配置",
                                padding=ModernTheme.PADDING_MEDIUM)
        hotkey_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_MEDIUM))

        modifiers, key = self.config_manager.get_hotkey_config()

        # 修饰键选择
        mod_frame = tk.Frame(hotkey_card.content_frame, bg=ModernTheme.SURFACE)
        mod_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            mod_frame,
            text="修饰键:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.modifier_var = tk.StringVar(value=modifiers)
        ttk.Combobox(
            mod_frame,
            textvariable=self.modifier_var,
            values=['ctrl', 'alt', 'shift', 'ctrl+alt', 'ctrl+shift', 'alt+shift'],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

        # 按键选择
        key_frame = tk.Frame(hotkey_card.content_frame, bg=ModernTheme.SURFACE)
        key_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            key_frame,
            text="按键:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.key_var = tk.StringVar(value=key)
        ttk.Combobox(
            key_frame,
            textvariable=self.key_var,
            values=['a', 'b', 'c', 'q', 'w', 'e', 'r', 's', '1', '2', '3', '4', '5'],
            state='readonly',
            width=10
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

    def _create_ai_settings(self, parent):
        """创建AI配置页面"""
        container = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_MEDIUM,
                      pady=ModernTheme.PADDING_MEDIUM)

        ai_config = self.config_manager.get_ai_config()

        # AI模型配置卡片
        ai_card = ModernCard(container, title="🤖 AI模型配置",
                             padding=ModernTheme.PADDING_MEDIUM)
        ai_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_MEDIUM))

        # 模型选择
        model_frame = tk.Frame(ai_card.content_frame, bg=ModernTheme.SURFACE)
        model_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            model_frame,
            text="模型:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value=ai_config['model'])
        tk.Entry(
            model_frame,
            textvariable=self.model_var,
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.TEXT_PRIMARY,
            width=30
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

        # API密钥
        key_frame = tk.Frame(ai_card.content_frame, bg=ModernTheme.SURFACE)
        key_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            key_frame,
            text="API密钥:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.api_key_var = tk.StringVar(value=ai_config['api_key'])
        tk.Entry(
            key_frame,
            textvariable=self.api_key_var,
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.TEXT_PRIMARY,
            width=40,
            show='*'
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

    def _create_ocr_settings(self, parent):
        """创建OCR配置页面"""
        container = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_MEDIUM,
                      pady=ModernTheme.PADDING_MEDIUM)

        ocr_config = self.config_manager.get_ocr_config()

        # OCR配置卡片
        ocr_card = ModernCard(container, title="🔍 OCR配置",
                              padding=ModernTheme.PADDING_MEDIUM)
        ocr_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_MEDIUM))

        # 语言设置
        lang_frame = tk.Frame(ocr_card.content_frame, bg=ModernTheme.SURFACE)
        lang_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            lang_frame,
            text="语言:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.lang_var = tk.StringVar(value=ocr_config.get('language', 'auto'))
        ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=['auto', 'zh', 'en', 'zh-en'],
            state='readonly',
            width=20
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

        # 置信度阈值
        conf_frame = tk.Frame(ocr_card.content_frame, bg=ModernTheme.SURFACE)
        conf_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            conf_frame,
            text="置信度阈值:",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        self.conf_var = tk.StringVar(value=str(ocr_config.get('confidence_threshold', 0.5)))
        tk.Entry(
            conf_frame,
            textvariable=self.conf_var,
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE_VARIANT,
            fg=ModernTheme.TEXT_PRIMARY,
            width=10
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_MEDIUM)

    def _create_notification_settings(self, parent):
        """创建通知配置页面"""
        container = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_MEDIUM,
                      pady=ModernTheme.PADDING_MEDIUM)

        # 通知配置卡片
        notification_card = ModernCard(container, title="🔔 系统通知配置",
                                       padding=ModernTheme.PADDING_MEDIUM)
        notification_card.pack(fill=tk.BOTH, expand=True, pady=(0, ModernTheme.PADDING_MEDIUM))

        # 说明文字
        info_text = "Windows系统通知会在AI答题完成后自动弹出，显示答案内容。"
        tk.Label(
            notification_card.content_frame,
            text=info_text,
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY
        ).pack(fill=tk.X, pady=ModernTheme.PADDING_MEDIUM)

        # 测试通知按钮
        test_button_frame = tk.Frame(notification_card.content_frame, bg=ModernTheme.SURFACE)
        test_button_frame.pack(fill=tk.X, pady=ModernTheme.PADDING_MEDIUM)

        ModernButton(
            test_button_frame,
            text="🔔 测试系统通知",
            command=self.test_notification,
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=ModernTheme.PADDING_SMALL)

        # 状态说明
        status_text = "注意: 系统通知功能需要在Windows 10/11上运行，并确保通知权限已开启。"
        tk.Label(
            notification_card.content_frame,
            text=status_text,
            font=('Arial', ModernTheme.FONT_SIZE_CAPTION),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_HINT
        ).pack(fill=tk.X, pady=ModernTheme.PADDING_SMALL)

    def test_notification(self):
        """测试通知功能"""
        try:
            # 动态导入通知管理器
            from core.notifier import WindowsNotifier
            notifier = WindowsNotifier()

            if notifier.is_available():
                # 显示测试通知
                notifier.test_notification()
                messagebox.showinfo("测试成功", "系统通知测试完成！请查看右下角的通知弹窗。")
            else:
                messagebox.showwarning("功能不可用", "系统通知功能不可用。\n\n可能原因：\n1. 不是Windows系统\n2. 未安装Windows-Toasts库\n\n请运行: pip install Windows-Toasts")
        except ImportError:
            messagebox.showerror("错误", "通知模块未找到，请确保程序完整。")

    def _create_about_tab(self, parent):
        """创建关于页面"""
        container = tk.Frame(parent, bg=ModernTheme.BACKGROUND)
        container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LARGE,
                      pady=ModernTheme.PADDING_LARGE)

        app_info = self.config_manager.get_app_info()

        # 应用信息
        tk.Label(
            container,
            text=app_info['name'],
            font=('Arial', ModernTheme.FONT_SIZE_H1, 'bold'),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(pady=ModernTheme.PADDING_LARGE)

        tk.Label(
            container,
            text=f"版本: {app_info['version']}",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_SECONDARY
        ).pack(pady=ModernTheme.PADDING_SMALL)

        tk.Label(
            container,
            text="智能截图OCR识别 + AI答题工具",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_HINT
        ).pack(pady=ModernTheme.PADDING_SMALL)

    def _on_ok(self):
        """确定按钮 - 保存配置"""
        try:
            # 保存快捷键配置
            self.config_manager.update_hotkey_config(
                self.modifier_var.get(),
                self.key_var.get()
            )

            # 保存AI配置
            self.config_manager.update_ai_config(
                model=self.model_var.get(),
                api_key=self.api_key_var.get()
            )

            # 保存OCR配置
            if hasattr(self, 'lang_var') and hasattr(self, 'conf_var'):
                try:
                    conf_value = float(self.conf_var.get())
                    # 这里需要添加保存OCR配置的方法
                    if hasattr(self.config_manager, 'update_ocr_config'):
                        self.config_manager.update_ocr_config(
                            language=self.lang_var.get(),
                            confidence_threshold=conf_value
                        )
                except ValueError:
                    messagebox.showerror("错误", "OCR置信度必须是数字")
                    return

            messagebox.showinfo("成功", "配置已保存")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")


class ModernMainWindow:
    """现代化主窗口"""

    def __init__(self, root):
        self.root = root
        self.root.title("截图答题工具")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # 设置窗口背景色
        self.root.config(bg=ModernTheme.BACKGROUND)

        # 初始化组件
        self.config_manager = None
        self.screenshot_manager = None
        self.region_manager = None
        self.ocr_manager = None
        self.ai_answer_manager = None
        self.hotkey_manager = None
        self.notifier = None

        # 创建界面
        self._setup_window()
        self._create_header()
        self._create_main_content()
        self._create_status_bar()

        # 延迟初始化系统组件
        self.root.after(100, self._initialize_system_components)

    def _setup_window(self):
        """设置窗口"""
        # 居中显示
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def _create_header(self):
        """创建头部"""
        header_frame = tk.Frame(self.root, bg=ModernTheme.SURFACE,
                                highlightbackground=ModernTheme.BORDER,
                                highlightthickness=1)
        header_frame.pack(fill=tk.X, padx=0, pady=0)

        # 内容容器
        header_content = tk.Frame(header_frame, bg=ModernTheme.SURFACE)
        header_content.pack(fill=tk.X, padx=ModernTheme.PADDING_LARGE,
                           pady=ModernTheme.PADDING_MEDIUM)

        # 标题
        tk.Label(
            header_content,
            text="📸 截图答题工具",
            font=('Arial', ModernTheme.FONT_SIZE_H2, 'bold'),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side=tk.LEFT)

        # 系统状态指示器
        self.status_indicator = tk.Label(
            header_content,
            text="●",
            font=('Arial', 12),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS
        )
        self.status_indicator.pack(side=tk.RIGHT)

    def _create_main_content(self):
        """创建主要内容区"""
        main_container = tk.Frame(self.root, bg=ModernTheme.BACKGROUND)
        main_container.pack(fill=tk.BOTH, expand=True, padx=ModernTheme.PADDING_LARGE,
                           pady=ModernTheme.PADDING_LARGE)

        # 核心操作卡片
        self._create_action_card(main_container)

        # 快捷键信息卡片
        self._create_shortcut_card(main_container)

        # 区域状态卡片
        self._create_region_status_card(main_container)

        # 功能按钮卡片
        self._create_function_buttons_card(main_container)

    def _create_action_card(self, parent):
        """创建核心操作卡片"""
        action_card = ModernCard(parent, padding=ModernTheme.PADDING_MEDIUM)
        action_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        # 大型截图按钮
        self.screenshot_button = ModernButton(
            action_card.content_frame,
            text="📷 截图答题",
            command=self.take_screenshot,
            style="primary",
            size="large",
            width_extra=60
        )
        self.screenshot_button.pack(pady=ModernTheme.PADDING_SMALL)

        # 状态提示
        self.status_label = tk.Label(
            action_card.content_frame,
            text="✅ 系统就绪",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS
        )
        self.status_label.pack(pady=2)

    def _create_shortcut_card(self, parent):
        """创建快捷键信息卡片"""
        shortcut_card = ModernCard(parent, title="⌨️ 快捷键",
                                   padding=ModernTheme.PADDING_SMALL)
        shortcut_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        self.hotkey_label = tk.Label(
            shortcut_card.content_frame,
            text="ALT + SHIFT + Q",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.PRIMARY
        )
        self.hotkey_label.pack(anchor=tk.W, pady=2)

    def _create_region_status_card(self, parent):
        """创建区域状态卡片"""
        region_card = ModernCard(parent, title="📏 区域状态",
                                padding=ModernTheme.PADDING_SMALL)
        region_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        self.region_label = tk.Label(
            region_card.content_frame,
            text="区域: 未设置",
            font=('Arial', ModernTheme.FONT_SIZE_BODY),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.ERROR
        )
        self.region_label.pack(anchor=tk.W, pady=2)

    def _create_function_buttons_card(self, parent):
        """创建功能按钮卡片"""
        button_card = ModernCard(parent, padding=ModernTheme.PADDING_SMALL)
        button_card.pack(fill=tk.X, pady=(0, ModernTheme.PADDING_SMALL))

        # 按钮容器
        button_row = tk.Frame(button_card.content_frame, bg=ModernTheme.SURFACE)
        button_row.pack(fill=tk.X)

        # 设置按钮
        ModernButton(
            button_row,
            text="⚙️ 设置",
            command=self.open_settings,
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=2)

        # 区域按钮
        ModernButton(
            button_row,
            text="🗺️ 区域",
            command=self.open_region_settings,
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=2)

        # 帮助按钮
        ModernButton(
            button_row,
            text="📖 帮助",
            command=self.show_help,
            style="secondary",
            size="medium"
        ).pack(side=tk.LEFT, padx=2)

    def _create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ModernStatusBar(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.set_info("v1.0.0")

    def _initialize_system_components(self):
        """初始化系统组件"""
        try:
            # 更新状态
            self.status_label.config(text="正在初始化系统组件...", fg=ModernTheme.INFO)
            self.root.update_idletasks()

            # 导入模块
            from config.config import ConfigManager
            from core.ocr import OCRManager
            from core.screenshot import ScreenshotManager
            from core.region import RegionManager
            from core.ai_answer import AIAnswerManager
            from core.notifier import WindowsNotifier
            from utils.hotkey import HotkeyManager

            # 初始化组件
            self.config_manager = ConfigManager()
            self.screenshot_manager = ScreenshotManager()
            self.region_manager = RegionManager()
            self.ocr_manager = OCRManager()
            self.ai_answer_manager = AIAnswerManager(self.config_manager)
            self.notifier = WindowsNotifier()
            self.hotkey_manager = HotkeyManager()

            # 设置快捷键
            self._setup_hotkey()

            # 启动鼠标监听器
            from pynput import mouse
            self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
            self.mouse_listener.start()

            # 更新快捷键显示
            self._update_hotkey_display()

            # 更新系统状态
            self._update_system_status()

        except Exception as e:
            self.status_label.config(text=f"初始化失败: {str(e)}", fg=ModernTheme.ERROR)
            print(f"初始化失败: {e}")

    def _setup_hotkey(self):
        """设置快捷键"""
        modifiers, key = self.config_manager.get_hotkey_config()
        hotkey_config = {'modifiers': modifiers, 'key': key}

        self.hotkey_manager.set_hotkey_config(hotkey_config)
        self.hotkey_manager.set_hotkey_callback(self.take_screenshot)
        self.hotkey_manager.set_region_callback(self.handle_region_shortcut)
        self.hotkey_manager.start_listener()

    def _update_hotkey_display(self):
        """更新快捷键显示"""
        if self.config_manager:
            modifiers, key = self.config_manager.get_hotkey_config()
            hotkey_text = f"{modifiers.upper().replace('+', ' + ')} + {key.upper()}"
            self.hotkey_label.config(text=hotkey_text)

    def _update_system_status(self):
        """更新系统状态"""
        region_complete = self.region_manager.is_region_complete()
        ai_available = self.ai_answer_manager.is_available()

        if region_complete and ai_available:
            self.status_indicator.config(fg=ModernTheme.SUCCESS)
            self.status_label.config(
                text="✅ 系统就绪，可以开始使用",
                fg=ModernTheme.SUCCESS
            )
            self.status_bar.set_status("系统就绪", "success")
        elif ai_available:
            self.status_indicator.config(fg=ModernTheme.WARNING)
            self.status_label.config(
                text="⚠️ 建议设置答题区域以获得更好体验",
                fg=ModernTheme.WARNING
            )
            self.status_bar.set_status("建议设置区域", "warning")
        else:
            self.status_indicator.config(fg=ModernTheme.ERROR)
            self.status_label.config(
                text="❌ 请先配置API密钥",
                fg=ModernTheme.ERROR
            )
            self.status_bar.set_status("需要配置", "error")

        # 更新区域显示
        self._update_region_display()

    def _update_region_display(self):
        """更新区域显示"""
        if self.region_manager:
            region_info, color = self.region_manager.get_region_info()
            self.region_label.config(text=f"📏 {region_info}", fg=color)

    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if self.region_manager.is_setting_mode() and pressed and button == mouse.Button.left:
            self.root.after(0, lambda: self.record_position_by_click(x, y))

    def record_position_by_click(self, x, y):
        """通过鼠标点击记录位置"""
        success, message = self.region_manager.record_position_by_click(x, y)
        if success:
            self._update_region_display()
            self.status_label.config(text=f"[成功] {message}", fg=ModernTheme.SUCCESS)
        else:
            self.status_label.config(text=f"[错误] {message}", fg=ModernTheme.ERROR)

    def handle_region_shortcut(self, digit_value):
        """处理区域设置快捷键 - 保留重要功能"""
        point_num = int(digit_value)
        success, message = self.region_manager.set_point_by_shortcut(point_num)
        if success:
            self._update_region_display()
            self.status_label.config(text=f"[成功] {message}", fg=ModernTheme.SUCCESS)
        else:
            self.status_label.config(text=f"[错误] {message}", fg=ModernTheme.ERROR)

    def take_screenshot(self):
        """截取屏幕并进行OCR识别"""
        try:
            import threading

            # 更新状态
            self.status_label.config(text="正在截图...", fg=ModernTheme.INFO)
            self.root.update_idletasks()

            # 获取截图区域
            bbox = self.region_manager.get_bbox()

            # 执行截图
            success, filepath, region_text, error = self.screenshot_manager.take_screenshot(bbox)

            if not success:
                self.status_label.config(text=f"[错误] {error}", fg=ModernTheme.ERROR)
                return

            # 更新状态
            self.status_label.config(
                text=f"[成功] 截图已保存，正在OCR识别...",
                fg=ModernTheme.SUCCESS
            )
            self.root.update_idletasks()

            # 在后台线程中处理OCR和AI
            ocr_thread = threading.Thread(
                target=self._process_ocr_and_ai,
                args=(filepath,),
                daemon=True
            )
            ocr_thread.start()

        except Exception as e:
            self.status_label.config(
                text=f"[错误] 截图失败: {str(e)}",
                fg=ModernTheme.ERROR
            )
            print(f"截图失败: {e}")

    def _process_ocr_and_ai(self, filepath):
        """在后台处理OCR和AI"""
        try:
            # OCR识别
            if self.ocr_manager.is_available():
                ocr_text = self.ocr_manager.recognize_text(filepath)
                if ocr_text:
                    txt_path = self.ocr_manager.save_result(ocr_text, filepath)

                    # 更新UI状态
                    self.root.after(0, lambda: self.status_label.config(
                        text="[成功] OCR识别完成，正在AI答题...",
                        fg=ModernTheme.INFO
                    ))

                    # AI答题
                    ai_result = self.ai_answer_manager.get_answer(ocr_text)

                    # 显示结果
                    self.root.after(0, lambda: self.show_ocr_result(
                        ocr_text, filepath, txt_path, ai_result
                    ))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="[成功] 截图完成，OCR未识别到文本",
                        fg=ModernTheme.SUCCESS
                    ))
            else:
                self.root.after(0, lambda: self.status_label.config(
                    text="[成功] 截图完成，OCR不可用",
                    fg=ModernTheme.WARNING
                ))

        except Exception as e:
            error_msg = f"[错误] 处理失败: {str(e)}"
            self.root.after(0, lambda: self.status_label.config(
                text=error_msg,
                fg=ModernTheme.ERROR
            ))
            print(f"处理失败: {e}")

    def show_ocr_result(self, ocr_text, image_path, txt_path=None, ai_result=None):
        """显示OCR结果"""
        try:
            from ui.modern_ui import ModernResultDialog
            dialog = ModernResultDialog(self.root, ocr_text, image_path, ai_result)

            # 显示系统通知
            if ai_result and ai_result.get('status') == 'success':
                answer = ai_result.get('answer', '无答案')
                self.notifier.show_answer_notification(answer, 'success')
                self.status_label.config(
                    text=f"[成功] AI答题完成: {answer}",
                    fg=ModernTheme.SUCCESS
                )
            else:
                self.status_label.config(
                    text="[成功] OCR识别完成",
                    fg=ModernTheme.SUCCESS
                )

        except Exception as e:
            print(f"显示结果失败: {e}")
            self.status_label.config(
                text=f"[错误] 显示结果失败: {e}",
                fg=ModernTheme.ERROR
            )

    def open_settings(self):
        """打开设置对话框"""
        try:
            from ui.modern_ui import ModernSettingsDialog
            dialog = ModernSettingsDialog(self.root, self.config_manager)
            self.root.wait_window(dialog)

            # 更新显示
            self._update_hotkey_display()
            self._update_system_status()

        except Exception as e:
            print(f"打开设置失败: {e}")

    def open_region_settings(self):
        """打开区域设置对话框"""
        try:
            from ui.modern_ui import ModernRegionDialog
            dialog = ModernRegionDialog(
                self.root,
                self.region_manager,
                self._update_region_display
            )
            self.root.wait_window(dialog)

        except Exception as e:
            print(f"打开区域设置失败: {e}")

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
• ESC：取消设置模式

📋 功能说明：
• 区域设置：固定答题区域，提高效率
• 配置管理：自定义AI模型、参数等
• 状态指示：绿色=正常，红色=需配置

💡 提示：
首次使用建议先配置区域，然后就可以一键答题了！"""
        messagebox.showinfo("使用帮助", help_text)

    def cleanup(self):
        """清理资源"""
        if self.hotkey_manager:
            self.hotkey_manager.stop_listener()
        if hasattr(self, 'mouse_listener') and self.mouse_listener.is_alive():
            self.mouse_listener.stop()