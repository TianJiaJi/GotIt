"""GotIt desktop workbench UI."""

from __future__ import annotations

import os
import queue
import subprocess
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk


# 跨平台字体配置：Windows 使用微软雅黑，Mac/Linux 使用 Arial
# 微软雅黑是 Windows 系统原生的中文字体，渲染效果最佳
if sys.platform == "win32":
    FONT_FAMILY = "Microsoft YaHei UI"
    # Windows 上增加字体大小，因为微软雅黑渲染较细
    FONT_SCALE = 1.2
else:
    FONT_FAMILY = "Arial"
    FONT_SCALE = 1.0


class Theme:
    BG = "#F3F5F9"
    SURFACE = "#FFFFFF"
    SIDEBAR = "#111827"
    SIDEBAR_HOVER = "#1F2937"
    PRIMARY = "#4F46E5"
    PRIMARY_HOVER = "#4338CA"
    PRIMARY_SOFT = "#EEF2FF"
    TEXT = "#111827"
    MUTED = "#667085"
    BORDER = "#E4E7EC"
    SUCCESS = "#12B76A"
    WARNING = "#F79009"
    ERROR = "#F04438"
    INFO = "#2E90FA"


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Theme.BG, **kwargs)
        self.canvas = tk.Canvas(self, bg=Theme.BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.content = tk.Frame(self.canvas, bg=Theme.BG)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.content.bind("<Configure>", self._update_scrollregion)
        self.content.bind("<Enter>", self._enable_mousewheel)
        self.content.bind("<Leave>", self._disable_mousewheel)
        self.canvas.bind("<Configure>", self._resize_content)
        self.canvas.bind("<Enter>", self._enable_mousewheel)
        self.canvas.bind("<Leave>", self._disable_mousewheel)

    def _update_scrollregion(self, _event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def _enable_mousewheel(self, _event=None):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", lambda _event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda _event: self.canvas.yview_scroll(1, "units"))

    def _disable_mousewheel(self, _event=None):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if abs(event.delta) >= 120:
            units = int(-event.delta / 120)
        else:
            units = -1 if event.delta > 0 else 1
        self.canvas.yview_scroll(units, "units")


class RegionSelector(tk.Toplevel):
    """Fullscreen drag selector for a single display."""

    def __init__(self, parent, on_selected, on_cancel):
        super().__init__(parent)
        self.on_selected = on_selected
        self.on_cancel = on_cancel
        self.start = None
        self.rectangle = None
        self.overrideredirect(True)
        self.attributes("-fullscreen", True)
        self.attributes("-topmost", True)
        try:
            self.attributes("-alpha", 0.32)
        except tk.TclError:
            pass
        self.configure(bg="black")

        self.canvas = tk.Canvas(self, bg="black", cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_text(
            self.winfo_screenwidth() // 2,
            42,
            text="拖动鼠标框选答题区域，按 Esc 取消",
            fill="white",
            font=(FONT_FAMILY, 22, "bold"),
        )
        self.canvas.bind("<ButtonPress-1>", self._start)
        self.canvas.bind("<B1-Motion>", self._drag)
        self.canvas.bind("<ButtonRelease-1>", self._finish)
        self.bind("<Escape>", self._cancel)
        self.focus_force()

    def _start(self, event):
        self.start = (event.x, event.y)
        if self.rectangle:
            self.canvas.delete(self.rectangle)
        self.rectangle = self.canvas.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#818CF8",
            width=4,
            fill="#4F46E5",
            stipple="gray25",
        )

    def _drag(self, event):
        if self.start and self.rectangle:
            self.canvas.coords(self.rectangle, self.start[0], self.start[1], event.x, event.y)

    def _finish(self, event):
        if not self.start:
            return
        left, right = sorted((self.start[0], event.x))
        top, bottom = sorted((self.start[1], event.y))
        if right - left < 10 or bottom - top < 10:
            self._cancel()
            return
        offset_x = self.winfo_rootx()
        offset_y = self.winfo_rooty()
        bbox = (left + offset_x, top + offset_y, right + offset_x, bottom + offset_y)
        self.destroy()
        self.on_selected(bbox)

    def _cancel(self, _event=None):
        self.destroy()
        self.on_cancel()


class ResultDialog(tk.Toplevel):
    # 题目类型显示名称映射
    TYPE_NAMES = {
        "single_choice": "单选题",
        "multiple_choice": "多选题",
        "true_false": "判断题",
        "essay": "解答题",
        "unknown": "未知类型"
    }

    def __init__(self, parent, result):
        super().__init__(parent)
        self.result = result
        self.title("处理详情")
        self.geometry("720x600")
        self.minsize(620, 500)
        self.configure(bg=Theme.BG)
        self.transient(parent)
        self.grab_set()
        self._build()

    def _build(self):
        container = tk.Frame(self, bg=Theme.BG)
        container.pack(fill="both", expand=True, padx=24, pady=22)

        tk.Label(
            container,
            text="处理详情",
            bg=Theme.BG,
            fg=Theme.TEXT,
            font=(FONT_FAMILY, 26, "bold"),
        ).pack(anchor="w")

        answer = self.result.answer
        if answer:
            # 显示题目类型
            type_name = self.TYPE_NAMES.get(self.result.question_type, "未知类型")
            type_label = tk.Label(
                container,
                text=f"题目类型: {type_name}",
                bg=Theme.BG,
                fg=Theme.PRIMARY,
                font=(FONT_FAMILY, 14),
                anchor="w"
            )
            type_label.pack(fill="x", pady=(8, 0))

            # 解答题提示
            if self.result.is_essay_question:
                tk.Label(
                    container,
                    text="✓ 答案已自动复制到剪贴板",
                    bg=Theme.BG,
                    fg=Theme.SUCCESS,
                    font=(FONT_FAMILY, 13),
                    anchor="w"
                ).pack(fill="x", pady=(4, 0))

            card = self._card(container, "AI 答案")
            tk.Label(
                card,
                text=answer,
                bg=Theme.PRIMARY_SOFT,
                fg=Theme.TEXT,
                justify="left",
                anchor="w",
                wraplength=620,
                padx=16,
                pady=14,
                font=(FONT_FAMILY, 17, "bold"),
            ).pack(fill="x")

        card = self._card(container, "OCR 识别文本", expand=True)
        text = scrolledtext.ScrolledText(
            card,
            height=14,
            wrap="word",
            font=(FONT_FAMILY, 14),
            relief="flat",
            bg="#F9FAFB",
            fg=Theme.TEXT,
            padx=12,
            pady=12,
        )
        text.pack(fill="both", expand=True)
        text.insert("1.0", self.result.ocr_text or "无识别文本")
        text.configure(state="disabled")

        path_text = self.result.screenshot_path or ""
        tk.Label(
            container,
            text=path_text,
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
            anchor="w",
        ).pack(fill="x", pady=(12, 0))

        buttons = tk.Frame(container, bg=Theme.BG)
        buttons.pack(fill="x", pady=(14, 0))
        tk.Button(
            buttons,
            text="关闭",
            command=self.destroy,
            bg=Theme.PRIMARY,
            fg="white",
            activebackground=Theme.PRIMARY_HOVER,
            activeforeground="white",
            relief="flat",
            padx=24,
            pady=9,
            font=(FONT_FAMILY, 13, "bold"),
            cursor="hand2",
        ).pack(side="right")

    @staticmethod
    def _card(parent, title, expand=False):
        frame = tk.Frame(
            parent,
            bg=Theme.SURFACE,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        frame.pack(fill="both" if expand else "x", expand=expand, pady=(16, 0))
        tk.Label(
            frame,
            text=title,
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12, "bold"),
        ).pack(anchor="w", padx=16, pady=(12, 8))
        body = tk.Frame(frame, bg=Theme.SURFACE)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        return body


class ModernMainWindow:
    """Main application controller and view."""

    def __init__(self, root, enable_tray=True):
        self.root = root
        self.root.title("GotIt - 截图答题工具")
        self.root.geometry("940x780")
        self.root.minsize(860, 700)
        self.root.configure(bg=Theme.BG)

        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="gotit")
        self.event_queue = queue.Queue()
        self.capture_busy = False
        self.chat_busy = False
        self.latest_result = None
        self.latest_chat_answer = ""
        self.hotkey_manager = None
        self.nav_buttons = {}
        self.pages = {}
        self._restoring_after_capture = False
        self.tray_enabled = enable_tray
        self.tray_icon = None

        self._setup_style()
        self._build_layout()
        self.root.after(80, self._initialize_components)

    def _setup_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(
            "GotIt.Horizontal.TProgressbar",
            troughcolor="#E9ECF2",
            background=Theme.PRIMARY,
            borderwidth=0,
            thickness=7,
        )
        style.configure("TCombobox", padding=5, font=(FONT_FAMILY, 12))
        style.configure("TCheckbutton", background=Theme.SURFACE, foreground=Theme.TEXT, font=(FONT_FAMILY, 12))
        style.configure("TLabel", font=(FONT_FAMILY, 12))
        style.configure("TButton", font=(FONT_FAMILY, 12))

    def _build_layout(self):
        self.sidebar = tk.Frame(self.root, bg=Theme.SIDEBAR, width=210)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        brand = tk.Frame(self.sidebar, bg=Theme.SIDEBAR)
        brand.pack(fill="x", padx=22, pady=(28, 32))
        tk.Label(
            brand,
            text="GotIt",
            bg=Theme.SIDEBAR,
            fg="white",
            font=(FONT_FAMILY, 28, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand,
            text="看见问题，直接得到答案",
            bg=Theme.SIDEBAR,
            fg="#98A2B3",
            font=(FONT_FAMILY, 13),
        ).pack(anchor="w", pady=(4, 0))

        self._nav_button("capture", "截图答题")
        self._nav_button("chat", "文字对话")
        self._nav_button("settings", "设置")

        status_box = tk.Frame(self.sidebar, bg="#182230")
        status_box.pack(side="bottom", fill="x", padx=14, pady=16)
        self.sidebar_status_dot = tk.Label(
            status_box,
            text="●",
            bg="#182230",
            fg=Theme.WARNING,
            font=(FONT_FAMILY, 12),
        )
        self.sidebar_status_dot.pack(side="left", padx=(12, 8), pady=12)
        self.sidebar_status = tk.Label(
            status_box,
            text="正在初始化",
            bg="#182230",
            fg="#D0D5DD",
            font=(FONT_FAMILY, 12),
        )
        self.sidebar_status.pack(side="left", pady=12)

        self.content = tk.Frame(self.root, bg=Theme.BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages["capture"] = self._build_capture_page()
        self.pages["chat"] = self._build_chat_page()
        self.pages["settings"] = self._build_settings_page()
        self.show_page("capture")

    def _nav_button(self, page, text):
        button = tk.Button(
            self.sidebar,
            text=text,
            command=lambda: self.show_page(page),
            anchor="w",
            bg=Theme.SIDEBAR,
            fg="#D0D5DD",
            activebackground=Theme.SIDEBAR_HOVER,
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=24,
            pady=13,
            font=(FONT_FAMILY, 13),
            cursor="hand2",
        )
        button.pack(fill="x", padx=10, pady=2)
        self.nav_buttons[page] = button

    def show_page(self, page):
        for name, frame in self.pages.items():
            if name == page:
                frame.pack(fill="both", expand=True)
                self.nav_buttons[name].configure(bg=Theme.PRIMARY, fg="white")
            else:
                frame.pack_forget()
                self.nav_buttons[name].configure(bg=Theme.SIDEBAR, fg="#D0D5DD")

    def _page_shell(self, title, subtitle):
        page = tk.Frame(self.content, bg=Theme.BG)
        header = tk.Frame(page, bg=Theme.BG)
        header.pack(fill="x", padx=32, pady=(28, 20))
        tk.Label(
            header,
            text=title,
            bg=Theme.BG,
            fg=Theme.TEXT,
            font=(FONT_FAMILY, 29, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text=subtitle,
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 13),
        ).pack(anchor="w", pady=(5, 0))
        return page

    def _card(self, parent, title=None, subtitle=None):
        card = tk.Frame(
            parent,
            bg=Theme.SURFACE,
            highlightbackground=Theme.BORDER,
            highlightthickness=1,
        )
        if title:
            heading = tk.Frame(card, bg=Theme.SURFACE)
            heading.pack(fill="x", padx=20, pady=(17, 10))
            tk.Label(
                heading,
                text=title,
                bg=Theme.SURFACE,
                fg=Theme.TEXT,
                font=(FONT_FAMILY, 15, "bold"),
            ).pack(anchor="w")
            if subtitle:
                tk.Label(
                    heading,
                    text=subtitle,
                    bg=Theme.SURFACE,
                    fg=Theme.MUTED,
                    font=(FONT_FAMILY, 12),
                ).pack(anchor="w", pady=(3, 0))
        body = tk.Frame(card, bg=Theme.SURFACE)
        body.pack(fill="both", expand=True, padx=20, pady=(4, 18))
        return card, body

    def _action_button(self, parent, text, command, primary=False, width=None):
        bg = Theme.PRIMARY if primary else "#F2F4F7"
        fg = "white" if primary else Theme.TEXT
        active = Theme.PRIMARY_HOVER if primary else "#E4E7EC"
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=active,
            activeforeground=fg,
            disabledforeground="#98A2B3",
            relief="flat",
            bd=0,
            padx=18,
            pady=10,
            width=width,
            font=(FONT_FAMILY, 13, "bold" if primary else "normal"),
            cursor="hand2",
        )
        return button

    def _build_capture_page(self):
        page = self._page_shell("截图答题", "框选题目区域，一次完成截图、识别和答题")
        body = tk.Frame(page, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        action_card, action = self._card(
            body,
            "开始处理",
            "支持完整答题和仅文字识别；执行期间不会重复启动任务",
        )
        action_card.pack(fill="x")

        buttons = tk.Frame(action, bg=Theme.SURFACE)
        buttons.pack(fill="x")
        self.capture_button = self._action_button(
            buttons,
            "截图并回答",
            lambda: self.start_capture(True),
            primary=True,
            width=16,
        )
        self.capture_button.pack(side="left")
        self.ocr_button = self._action_button(
            buttons,
            "仅识别文字",
            lambda: self.start_capture(False),
            width=14,
        )
        self.ocr_button.pack(side="left", padx=(10, 0))
        self.capture_stage = tk.Label(
            buttons,
            text="准备就绪",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
        )
        self.capture_stage.pack(side="right")

        self.progress = ttk.Progressbar(
            action,
            mode="indeterminate",
            style="GotIt.Horizontal.TProgressbar",
        )
        self.progress.pack(fill="x", pady=(16, 0))

        middle = tk.Frame(body, bg=Theme.BG)
        middle.pack(fill="x", pady=14)
        middle.grid_columnconfigure(0, weight=1)
        middle.grid_columnconfigure(1, weight=1)

        region_card, region = self._card(middle, "截图区域", "未设置时默认截取整个屏幕")
        region_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        self.region_status = tk.Label(
            region,
            text="正在加载区域...",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            anchor="w",
            justify="left",
            wraplength=270,
            font=(FONT_FAMILY, 13),
        )
        self.region_status.pack(fill="x", pady=(0, 12))
        region_buttons = tk.Frame(region, bg=Theme.SURFACE)
        region_buttons.pack(fill="x")
        self._action_button(region_buttons, "拖动框选", self.select_region, primary=True).pack(side="left")
        self._action_button(region_buttons, "清除", self.clear_region).pack(side="left", padx=(8, 0))

        shortcut_card, shortcut = self._card(middle, "快捷操作", "全局快捷键可在其他窗口中使用")
        shortcut_card.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        self.hotkey_display = tk.Label(
            shortcut,
            text="正在加载...",
            bg=Theme.SURFACE,
            fg=Theme.PRIMARY,
            anchor="w",
            font=(FONT_FAMILY, 15, "bold"),
        )
        self.hotkey_display.pack(fill="x")
        tk.Label(
            shortcut,
            text="Alt+Ctrl+1/2 设置区域两点\nCtrl+Shift+1 处理剪贴板文本",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            justify="left",
            anchor="w",
            font=(FONT_FAMILY, 12),
        ).pack(fill="x", pady=(9, 0))

        result_card, result = self._card(body, "最近结果", "处理完成后可快速复制或查看识别详情")
        result_card.pack(fill="both", expand=True)

        # 题目类型提示标签
        self.question_type_label = tk.Label(
            result,
            text="",
            bg=Theme.SURFACE,
            fg=Theme.PRIMARY,
            font=(FONT_FAMILY, 12),
            anchor="w"
        )
        self.question_type_label.pack(fill="x", padx=14, pady=(8, 0))

        self.answer_text = tk.Label(
            result,
            text="还没有结果",
            bg="#F9FAFB",
            fg=Theme.MUTED,
            anchor="w",
            justify="left",
            wraplength=610,
            padx=16,
            pady=16,
            font=(FONT_FAMILY, 16),
        )
        self.answer_text.pack(fill="both", expand=True)
        result_buttons = tk.Frame(result, bg=Theme.SURFACE)
        result_buttons.pack(fill="x", pady=(12, 0))
        self.copy_result_button = self._action_button(result_buttons, "复制结果", self.copy_latest_result)
        self.copy_result_button.configure(state="disabled")
        self.copy_result_button.pack(side="left")
        self.detail_button = self._action_button(result_buttons, "查看详情", self.show_result_detail)
        self.detail_button.configure(state="disabled")
        self.detail_button.pack(side="left", padx=(8, 0))
        self.open_output_button = self._action_button(result_buttons, "打开输出目录", self.open_output_directory)
        self.open_output_button.pack(side="right")
        return page

    def _build_chat_page(self):
        page = self._page_shell("文字对话", "输入或粘贴文本，保留最近上下文进行连续问答")
        body = tk.Frame(page, bg=Theme.BG)
        body.pack(fill="both", expand=True, padx=32, pady=(0, 28))

        input_card, input_body = self._card(body, "你的问题", "也可以读取当前剪贴板内容")
        input_card.pack(fill="x")
        self.chat_input = scrolledtext.ScrolledText(
            input_body,
            height=7,
            wrap="word",
            relief="flat",
            bg="#F9FAFB",
            fg=Theme.TEXT,
            insertbackground=Theme.TEXT,
            padx=12,
            pady=10,
            font=(FONT_FAMILY, 14),
        )
        self.chat_input.pack(fill="x")
        chat_actions = tk.Frame(input_body, bg=Theme.SURFACE)
        chat_actions.pack(fill="x", pady=(12, 0))
        self.chat_send_button = self._action_button(
            chat_actions,
            "发送问题",
            self.send_chat,
            primary=True,
            width=12,
        )
        self.chat_send_button.pack(side="left")
        self._action_button(chat_actions, "读取剪贴板", self.load_clipboard).pack(side="left", padx=(8, 0))
        self.chat_status = tk.Label(
            chat_actions,
            text="上下文 0 条",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
        )
        self.chat_status.pack(side="right")

        output_card, output_body = self._card(body, "AI 回答", "回答可一键复制回剪贴板")
        output_card.pack(fill="both", expand=True, pady=(14, 0))
        self.chat_output = scrolledtext.ScrolledText(
            output_body,
            height=13,
            wrap="word",
            relief="flat",
            bg="#F9FAFB",
            fg=Theme.TEXT,
            padx=12,
            pady=10,
            font=(FONT_FAMILY, 14),
            state="disabled",
        )
        self.chat_output.pack(fill="both", expand=True)
        output_actions = tk.Frame(output_body, bg=Theme.SURFACE)
        output_actions.pack(fill="x", pady=(12, 0))
        self._action_button(output_actions, "复制回答", self.copy_chat_answer).pack(side="left")
        self._action_button(output_actions, "清空上下文", self.clear_chat_context).pack(side="right")
        return page

    def _field(self, parent, label, variable, secret=False, width=32):
        row = tk.Frame(parent, bg=Theme.SURFACE)
        row.pack(fill="x", pady=6)
        tk.Label(
            row,
            text=label,
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            width=13,
            anchor="w",
            font=(FONT_FAMILY, 12),
        ).pack(side="left")
        entry = tk.Entry(
            row,
            textvariable=variable,
            show="*" if secret else "",
            width=width,
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=(FONT_FAMILY, 13),
        )
        entry.pack(side="left", fill="x", expand=True, ipady=7)
        return entry

    def _build_settings_page(self):
        page = self._page_shell("设置", "配置模型、识别精度和软件行为，保存后立即生效")
        scroll = ScrollableFrame(page)
        scroll.pack(fill="both", expand=True, padx=32, pady=(0, 24))
        body = scroll.content

        self.model_var = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.api_base_var = tk.StringVar()
        self.temperature_var = tk.StringVar()
        self.max_tokens_var = tk.StringVar()
        self.confidence_var = tk.StringVar()
        self.hide_window_var = tk.BooleanVar()
        self.show_popup_var = tk.BooleanVar()
        self.notification_var = tk.BooleanVar()
        self.delay_var = tk.StringVar()
        self.modifier_var = tk.StringVar()
        self.hotkey_var = tk.StringVar()

        ai_card, ai = self._card(body, "AI 模型", "支持 OpenAI 兼容的模型服务地址")
        ai_card.pack(fill="x")
        self._field(ai, "模型名称", self.model_var)
        self.api_key_entry = self._field(ai, "API 密钥", self.api_key_var, secret=True)
        self._field(ai, "API 地址", self.api_base_var)
        parameter_row = tk.Frame(ai, bg=Theme.SURFACE)
        parameter_row.pack(fill="x", pady=6)
        tk.Label(
            parameter_row,
            text="温度",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            width=13,
            anchor="w",
            font=(FONT_FAMILY, 12),
        ).pack(side="left")
        tk.Entry(parameter_row, textvariable=self.temperature_var, width=8, relief="solid", bd=1).pack(
            side="left", ipady=7
        )
        tk.Label(
            parameter_row,
            text="最大输出",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
        ).pack(side="left", padx=(22, 8))
        tk.Entry(parameter_row, textvariable=self.max_tokens_var, width=10, relief="solid", bd=1).pack(
            side="left", ipady=7
        )
        self._action_button(
            parameter_row,
            "显示/隐藏密钥",
            self.toggle_api_key,
        ).pack(side="right")

        behavior_card, behavior = self._card(body, "软件行为", "优化截图体验和结果反馈方式")
        behavior_card.pack(fill="x", pady=(14, 0))
        ttk.Checkbutton(behavior, text="截图时自动隐藏主窗口", variable=self.hide_window_var).pack(
            anchor="w", pady=5
        )
        ttk.Checkbutton(behavior, text="答题完成后显示详情弹窗", variable=self.show_popup_var).pack(
            anchor="w", pady=5
        )
        ttk.Checkbutton(behavior, text="启用系统通知", variable=self.notification_var).pack(
            anchor="w", pady=5
        )
        delay_row = tk.Frame(behavior, bg=Theme.SURFACE)
        delay_row.pack(fill="x", pady=(8, 0))
        tk.Label(
            delay_row,
            text="截图延迟（毫秒）",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
        ).pack(side="left")
        tk.Entry(delay_row, textvariable=self.delay_var, width=10, relief="solid", bd=1).pack(
            side="left", padx=(12, 0), ipady=7
        )

        advanced_card, advanced = self._card(body, "识别与快捷键")
        advanced_card.pack(fill="x", pady=(14, 0))
        row = tk.Frame(advanced, bg=Theme.SURFACE)
        row.pack(fill="x", pady=6)
        tk.Label(
            row,
            text="OCR 置信度",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            width=16,
            anchor="w",
            font=(FONT_FAMILY, 12),
        ).pack(side="left")
        tk.Entry(row, textvariable=self.confidence_var, width=10, relief="solid", bd=1).pack(
            side="left", ipady=7
        )
        tk.Label(
            row,
            text="范围 0 到 1，越高越严格",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            font=(FONT_FAMILY, 12),
        ).pack(side="left", padx=(10, 0))

        hotkey_row = tk.Frame(advanced, bg=Theme.SURFACE)
        hotkey_row.pack(fill="x", pady=6)
        tk.Label(
            hotkey_row,
            text="截图快捷键",
            bg=Theme.SURFACE,
            fg=Theme.MUTED,
            width=16,
            anchor="w",
            font=(FONT_FAMILY, 12),
        ).pack(side="left")
        ttk.Combobox(
            hotkey_row,
            textvariable=self.modifier_var,
            values=("ctrl", "alt", "shift", "ctrl+alt", "ctrl+shift", "alt+shift"),
            state="readonly",
            width=14,
        ).pack(side="left")
        ttk.Combobox(
            hotkey_row,
            textvariable=self.hotkey_var,
            values=tuple("abcdefghijklmnopqrstuvwxyz123456789"),
            state="readonly",
            width=6,
        ).pack(side="left", padx=(8, 0))

        footer = tk.Frame(body, bg=Theme.BG)
        footer.pack(fill="x", pady=18)
        self.settings_message = tk.Label(
            footer,
            text="",
            bg=Theme.BG,
            fg=Theme.SUCCESS,
            font=(FONT_FAMILY, 12),
        )
        self.settings_message.pack(side="left")
        self._action_button(footer, "测试通知", self.test_notification).pack(side="right")
        self._action_button(footer, "保存设置", self.save_settings, primary=True).pack(
            side="right", padx=(0, 10)
        )
        return page

    def _initialize_components(self):
        try:
            from config.config import ConfigManager
            from core.ai_answer import AIAnswerManager
            from core.clipboard_chat import ClipboardChatManager
            from core.notifier import SystemNotifier
            from core.ocr import OCRManager
            from core.region import RegionManager
            from core.screenshot import ScreenshotManager
            from core.workflow import CaptureWorkflow

            # 获取图标路径（通知使用 JPG 格式）
            icon_path = Path(__file__).parent.parent / "assets" / "app_icon.jpg"

            self.config_manager = ConfigManager()
            capture_config = self.config_manager.get_capture_config()
            self.region_manager = RegionManager(capture_config.get("region"))
            self.screenshot_manager = ScreenshotManager()
            self.ocr_manager = OCRManager(self.config_manager)
            self.ai_answer_manager = AIAnswerManager(self.config_manager)
            self.clipboard_chat_manager = ClipboardChatManager(self.config_manager)
            self.notifier = SystemNotifier(icon_path=str(icon_path))
            self.workflow = CaptureWorkflow(
                self.screenshot_manager,
                self.ocr_manager,
                self.ai_answer_manager,
            )
            self._load_settings()
            self._setup_hotkeys()
            self._update_region_status()
            self._update_chat_status()
            self._update_system_status()
        except Exception as exc:
            self._set_system_status(f"初始化失败: {exc}", Theme.ERROR)
            messagebox.showerror("初始化失败", str(exc))

    def _setup_hotkeys(self):
        try:
            from utils.hotkey import HotkeyManager

            if not self.hotkey_manager:
                self.hotkey_manager = HotkeyManager()
                self.hotkey_manager.set_hotkey_callback(
                    lambda: self.root.after(0, lambda: self.start_capture(True))
                )
                self.hotkey_manager.set_region_callback(
                    lambda digit: self.root.after(0, lambda: self.set_region_point(digit))
                )
                self.hotkey_manager.set_clipboard_callback(
                    lambda: self.root.after(0, self.handle_clipboard_chat)
                )
                self.hotkey_manager.set_clear_context_callback(
                    lambda: self.root.after(0, self.clear_chat_context)
                )
                self.hotkey_manager.start_listener()
            modifiers, key = self.config_manager.get_hotkey_config()
            self.hotkey_manager.set_hotkey_config({"modifiers": modifiers, "key": key})
            self.hotkey_display.configure(
                text=f"{modifiers.upper().replace('+', ' + ')} + {key.upper()}"
            )
        except Exception as exc:
            self.hotkey_manager = None
            self.hotkey_display.configure(text="全局快捷键不可用", fg=Theme.WARNING)
            print(f"快捷键初始化失败: {exc}")

    def _load_settings(self):
        ai = self.config_manager.get_ai_config()
        ocr = self.config_manager.get_ocr_config()
        capture = self.config_manager.get_capture_config()
        display = self.config_manager.get_display_config()
        modifiers, key = self.config_manager.get_hotkey_config()
        self.model_var.set(ai["model"])
        self.api_key_var.set(ai["api_key"])
        self.api_base_var.set(ai["api_base"])
        self.temperature_var.set(str(ai["temperature"]))
        self.max_tokens_var.set(str(ai["max_tokens"]))
        self.confidence_var.set(str(ocr["confidence_threshold"]))
        self.hide_window_var.set(capture["hide_window"])
        self.delay_var.set(str(capture["delay_ms"]))
        self.show_popup_var.set(display["show_result_popup"])
        self.notification_var.set(display["notifications_enabled"])
        self.modifier_var.set(modifiers)
        self.hotkey_var.set(key)

    def _set_system_status(self, text, color):
        self.sidebar_status.configure(text=text)
        self.sidebar_status_dot.configure(fg=color)

    def _update_system_status(self):
        missing = []
        if not self.ocr_manager.is_available():
            missing.append("OCR")
        if not self.ai_answer_manager.is_available():
            missing.append("AI配置")
        if missing:
            self._set_system_status("需配置 " + " / ".join(missing), Theme.WARNING)
        else:
            self._set_system_status("系统就绪", Theme.SUCCESS)

    def _update_region_status(self):
        info, _color = self.region_manager.get_region_info()
        bbox = self.region_manager.get_bbox()
        color = Theme.SUCCESS if bbox else Theme.MUTED
        self.region_status.configure(text=info, fg=color)

    def select_region(self):
        if self.capture_busy:
            return
        self.root.withdraw()
        self.root.after(
            180,
            lambda: RegionSelector(self.root, self._region_selected, self._region_cancelled),
        )

    def _region_selected(self, bbox):
        self.region_manager.set_region(bbox)
        self.config_manager.update_capture_config(region=bbox)
        self.root.deiconify()
        self.root.lift()
        self._update_region_status()
        self.capture_stage.configure(text="区域已更新", fg=Theme.SUCCESS)

    def _region_cancelled(self):
        self.root.deiconify()
        self.root.lift()
        self.capture_stage.configure(text="已取消框选", fg=Theme.MUTED)

    def clear_region(self):
        self.region_manager.clear_region()
        self.config_manager.update_capture_config(clear_region=True)
        self._update_region_status()
        self.capture_stage.configure(text="已改为全屏截图", fg=Theme.MUTED)

    def set_region_point(self, digit):
        if not hasattr(self, "region_manager"):
            return
        success, message = self.region_manager.set_point_by_shortcut(int(digit))
        if success:
            bbox = self.region_manager.get_bbox()
            if bbox:
                self.config_manager.update_capture_config(region=bbox)
            self._update_region_status()
            self.capture_stage.configure(text=message, fg=Theme.SUCCESS)
        else:
            self.capture_stage.configure(text=message, fg=Theme.ERROR)

    def _set_capture_busy(self, busy):
        self.capture_busy = busy
        state = "disabled" if busy else "normal"
        self.capture_button.configure(state=state)
        self.ocr_button.configure(state=state)
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()

    def start_capture(self, include_ai=True):
        if self.capture_busy or not hasattr(self, "workflow"):
            return
        if include_ai and not self.ai_answer_manager.is_available():
            self.show_page("settings")
            self.settings_message.configure(text="请先填写可用的模型和 API 密钥", fg=Theme.ERROR)
            return
        if not self.ocr_manager.is_available():
            messagebox.showwarning("缺少 OCR 依赖", "请先安装 requirements.txt 中的依赖。")
            return

        self._set_capture_busy(True)
        self.capture_stage.configure(text="准备截图...", fg=Theme.INFO)
        capture_config = self.config_manager.get_capture_config()
        if capture_config["hide_window"]:
            self.root.withdraw()
            self._restoring_after_capture = True
        delay = capture_config["delay_ms"]
        self.root.after(delay, lambda: self._submit_capture(include_ai))

    def _submit_capture(self, include_ai):
        bbox = self.region_manager.get_bbox()
        future = self.executor.submit(
            self.workflow.run,
            bbox,
            include_ai,
            lambda stage: self.event_queue.put(("capture_stage", stage)),
        )
        self.root.after(60, lambda: self._poll_capture(future, include_ai))

    def _restore_window(self):
        if self._restoring_after_capture:
            self._restoring_after_capture = False
            self.root.deiconify()
            self.root.lift()

    def _poll_capture(self, future: Future, include_ai):
        self._drain_events()
        if not future.done():
            self.root.after(60, lambda: self._poll_capture(future, include_ai))
            return
        self._restore_window()
        self._set_capture_busy(False)
        try:
            result = future.result()
        except Exception as exc:
            self.capture_stage.configure(text=f"处理失败: {exc}", fg=Theme.ERROR)
            return
        self._handle_capture_result(result, include_ai)

    def _drain_events(self):
        stage_text = {
            "capture": "正在截图...",
            "ocr": "正在识别文字...",
            "ai": "正在生成答案...",
            "done": "处理完成",
        }
        try:
            while True:
                event, value = self.event_queue.get_nowait()
                if event == "capture_stage":
                    if value == "ocr":
                        self._restore_window()
                    self.capture_stage.configure(
                        text=stage_text.get(value, value),
                        fg=Theme.INFO if value != "done" else Theme.SUCCESS,
                    )
        except queue.Empty:
            pass

    def _handle_capture_result(self, result, include_ai):
        self.latest_result = result
        self.detail_button.configure(state="normal")
        display_text = result.answer if include_ai and result.answer else result.ocr_text
        if result.success:
            self.answer_text.configure(text=display_text, fg=Theme.TEXT, bg=Theme.PRIMARY_SOFT)
            self.copy_result_button.configure(state="normal")
            self.capture_stage.configure(text="处理完成", fg=Theme.SUCCESS)
            display = self.config_manager.get_display_config()

            # 显示题目类型
            type_names = {
                "single_choice": "单选题",
                "multiple_choice": "多选题",
                "true_false": "判断题",
                "essay": "解答题",
                "unknown": "未知类型"
            }
            type_name = type_names.get(result.question_type, "未知类型")
            if include_ai and result.question_type != "unknown":
                self.question_type_label.configure(text=f"题目类型: {type_name}")
            else:
                self.question_type_label.configure(text="")

            # 解答题自动复制答案到剪贴板
            if include_ai and result.is_essay_question and result.answer:
                self.root.clipboard_clear()
                self.root.clipboard_append(result.answer)
                self.capture_stage.configure(text="解答题答案已复制到剪贴板", fg=Theme.SUCCESS)

            if display["notifications_enabled"] and display_text:
                self.notifier.show_answer_notification(display_text, "success")
            if display["show_result_popup"]:
                ResultDialog(self.root, result)
        else:
            error = result.error or "处理失败"
            self.answer_text.configure(text=error, fg=Theme.ERROR, bg="#FEF3F2")
            self.copy_result_button.configure(state="disabled")
            self.capture_stage.configure(text=error, fg=Theme.ERROR)
            self.question_type_label.configure(text="")
            if self.config_manager.get_display_config()["notifications_enabled"]:
                self.notifier.show_answer_notification(error, "error")

    def copy_latest_result(self):
        if not self.latest_result:
            return
        text = self.latest_result.answer or self.latest_result.ocr_text
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.capture_stage.configure(text="结果已复制", fg=Theme.SUCCESS)

    def show_result_detail(self):
        if self.latest_result:
            ResultDialog(self.root, self.latest_result)

    def open_output_directory(self):
        output = Path(__file__).resolve().parents[2] / "outputs"
        output.mkdir(parents=True, exist_ok=True)
        try:
            if sys.platform == "win32":
                os.startfile(output)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", str(output)])
            else:
                subprocess.Popen(["xdg-open", str(output)])
        except OSError as exc:
            messagebox.showerror("无法打开目录", str(exc))

    def load_clipboard(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            self.chat_status.configure(text="剪贴板中没有文本", fg=Theme.ERROR)
            return
        self.chat_input.delete("1.0", "end")
        self.chat_input.insert("1.0", text)
        self.chat_input.focus_set()

    def send_chat(self):
        text = self.chat_input.get("1.0", "end").strip()
        self._start_chat(text, copy_to_clipboard=False)

    def handle_clipboard_chat(self):
        try:
            text = self.root.clipboard_get()
        except tk.TclError:
            self.chat_status.configure(text="剪贴板中没有文本", fg=Theme.ERROR)
            return
        self.show_page("chat")
        self.chat_input.delete("1.0", "end")
        self.chat_input.insert("1.0", text)
        self._start_chat(text, copy_to_clipboard=True)

    def _start_chat(self, text, copy_to_clipboard):
        if self.chat_busy or not text.strip():
            if not text.strip():
                self.chat_status.configure(text="请输入问题", fg=Theme.ERROR)
            return
        if not self.ai_answer_manager.is_available():
            self.show_page("settings")
            self.settings_message.configure(text="请先填写可用的模型和 API 密钥", fg=Theme.ERROR)
            return
        self.chat_busy = True
        self.chat_send_button.configure(state="disabled")
        self.chat_status.configure(text="正在生成回答...", fg=Theme.INFO)
        future = self.executor.submit(self.clipboard_chat_manager.process_clipboard_text, text)
        self.root.after(80, lambda: self._poll_chat(future, copy_to_clipboard))

    def _poll_chat(self, future, copy_to_clipboard):
        if not future.done():
            self.root.after(80, lambda: self._poll_chat(future, copy_to_clipboard))
            return
        self.chat_busy = False
        self.chat_send_button.configure(state="normal")
        try:
            result = future.result()
        except Exception as exc:
            result = {"status": "error", "message": str(exc)}

        if result.get("status") == "success":
            answer = result["answer"]
            self.latest_chat_answer = answer
            self.chat_output.configure(state="normal")
            self.chat_output.delete("1.0", "end")
            self.chat_output.insert("1.0", answer)
            self.chat_output.configure(state="disabled")
            self.chat_input.delete("1.0", "end")
            self._update_chat_status()
            if copy_to_clipboard:
                self.copy_chat_answer()
            if self.config_manager.get_display_config()["notifications_enabled"]:
                self.notifier.show_answer_notification("回答已生成并可复制", "success")
        else:
            self.chat_status.configure(text=result.get("message", "对话失败"), fg=Theme.ERROR)

    def copy_chat_answer(self):
        if not self.latest_chat_answer:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(self.latest_chat_answer)
        self.chat_status.configure(text="回答已复制到剪贴板", fg=Theme.SUCCESS)

    def clear_chat_context(self):
        if not hasattr(self, "clipboard_chat_manager"):
            return
        result = self.clipboard_chat_manager.clear_context()
        if result.get("status") == "success":
            self.latest_chat_answer = ""
            self.chat_output.configure(state="normal")
            self.chat_output.delete("1.0", "end")
            self.chat_output.configure(state="disabled")
            self._update_chat_status()
        else:
            self.chat_status.configure(text=result.get("message", "清空失败"), fg=Theme.ERROR)

    def _update_chat_status(self):
        count = self.clipboard_chat_manager.get_context_info()["total_messages"]
        self.chat_status.configure(text=f"上下文 {count} 条", fg=Theme.MUTED)

    def toggle_api_key(self):
        self.api_key_entry.configure(show="" if self.api_key_entry.cget("show") else "*")

    def save_settings(self):
        try:
            temperature = float(self.temperature_var.get())
            max_tokens = int(self.max_tokens_var.get())
            confidence = float(self.confidence_var.get())
            delay = int(self.delay_var.get())
            if not 0 <= temperature <= 2:
                raise ValueError("温度必须在 0 到 2 之间")
            if max_tokens < 1:
                raise ValueError("最大输出必须大于 0")
            if not 0 <= confidence <= 1:
                raise ValueError("OCR 置信度必须在 0 到 1 之间")
            if not 0 <= delay <= 5000:
                raise ValueError("截图延迟必须在 0 到 5000 毫秒之间")

            self.config_manager.update_ai_config(
                model=self.model_var.get().strip(),
                api_key=self.api_key_var.get().strip(),
                api_base=self.api_base_var.get().strip(),
                temperature=temperature,
                max_tokens=max_tokens,
            )
            self.config_manager.update_ocr_config(confidence_threshold=confidence)
            self.config_manager.update_capture_config(
                hide_window=self.hide_window_var.get(),
                delay_ms=delay,
            )
            self.config_manager.update_display_config(
                show_result_popup=self.show_popup_var.get(),
                notifications_enabled=self.notification_var.get(),
            )
            self.config_manager.update_hotkey_config(
                self.modifier_var.get(),
                self.hotkey_var.get(),
            )
            self.ai_answer_manager.reload_config()
            self.clipboard_chat_manager.reload_config()
            self._setup_hotkeys()
            self._update_system_status()
            self.settings_message.configure(text="设置已保存并立即生效", fg=Theme.SUCCESS)
        except ValueError as exc:
            self.settings_message.configure(text=str(exc), fg=Theme.ERROR)
        except Exception as exc:
            self.settings_message.configure(text=f"保存失败: {exc}", fg=Theme.ERROR)

    def test_notification(self):
        if self.notifier.is_available():
            self.notifier.test_notification()
            self.settings_message.configure(text="测试通知已发送", fg=Theme.SUCCESS)
        else:
            self.settings_message.configure(text="当前系统通知不可用", fg=Theme.WARNING)

    def cleanup(self):
        if self.hotkey_manager:
            self.hotkey_manager.stop_listener()
        self.executor.shutdown(wait=False, cancel_futures=True)
        if self.tray_icon:
            self.tray_icon.stop()

    def set_tray_icon(self, tray_icon):
        """设置系统托盘图标实例。"""
        self.tray_icon = tray_icon

    def hide_to_tray(self):
        """隐藏窗口到系统托盘。"""
        if self.tray_enabled and self.tray_icon:
            self.root.withdraw()
            if self.tray_icon.is_running:
                self.tray_icon.show_notification("GotIt", "程序已最小化到系统托盘")

    def show_from_tray(self):
        """从系统托盘恢复窗口。"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def on_window_close(self):
        """窗口关闭按钮事件处理。"""
        if self.tray_enabled and self.tray_icon and self.tray_icon.is_running:
            # 最小化到托盘而不是关闭
            self.hide_to_tray()
        else:
            # 真正关闭
            if hasattr(self, 'cleanup'):
                self.cleanup()
            self.root.destroy()
