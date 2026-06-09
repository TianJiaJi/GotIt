"""系统托盘图标管理模块。"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Optional

# pystray 在 macOS 上支持有限，但 Windows 和 Linux 上工作良好
try:
    import pystray
    from PIL import Image

    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class SystemTrayIcon:
    """系统托盘图标管理器。"""

    def __init__(
        self,
        icon_path: Path,
        show_window_callback: Callable[[], None],
        quit_callback: Callable[[], None],
        hide_to_tray_callback: Callable[[], None] = None,
    ):
        """
        初始化系统托盘图标。

        Args:
            icon_path: 图标文件路径
            show_window_callback: 显示窗口的回调函数
            quit_callback: 退出程序的回调函数
            hide_to_tray_callback: 隐藏到托盘的回调函数
        """
        self.icon_path = icon_path
        self.show_window_callback = show_window_callback
        self.quit_callback = quit_callback
        self.hide_to_tray_callback = hide_to_tray_callback
        self.icon: Optional[pystray.Icon] = None
        self.is_running = False

    def is_available(self) -> bool:
        """检查系统托盘是否可用。"""
        return PYSTRAY_AVAILABLE

    def create_menu(self) -> pystray.Menu:
        """创建托盘菜单。"""
        return pystray.Menu(
            pystray.MenuItem("显示窗口", self._on_show_window),
            pystray.MenuItem("隐藏到托盘", self._on_hide_to_tray),
            pystray.MenuItem("退出", self._on_quit),
        )

    def _on_show_window(self) -> None:
        """显示窗口菜单项回调。"""
        if self.show_window_callback:
            self.show_window_callback()

    def _on_hide_to_tray(self) -> None:
        """隐藏到托盘菜单项回调。"""
        if self.hide_to_tray_callback:
            self.hide_to_tray_callback()

    def _on_quit(self) -> None:
        """退出菜单项回调。"""
        if self.quit_callback:
            self.quit_callback()

    def start(self, window_hidden_callback: Callable[[], None] = None) -> bool:
        """
        启动系统托盘图标。

        Args:
            window_hidden_callback: 窗口隐藏时的回调函数

        Returns:
            是否成功启动
        """
        if not self.is_available():
            return False

        try:
            # 加载图标
            icon_image = Image.open(str(self.icon_path))

            # 创建托盘图标
            self.icon = pystray.Icon(
                name="GotIt",
                icon=icon_image,
                title="GotIt - 截图答题工具",
                menu=self.create_menu(),
            )

            # 设置默认点击行为（左键显示窗口）
            self.icon.on_activate = lambda: self._on_show_window()

            self.is_running = True
            return True
        except Exception as e:
            print(f"[警告] 系统托盘启动失败: {e}")
            return False

    def run(self) -> None:
        """运行托盘图标事件循环（阻塞）。"""
        if self.icon and self.is_running:
            self.icon.run()

    def stop(self) -> None:
        """停止系统托盘图标。"""
        if self.icon and self.is_running:
            self.is_running = False
            self.icon.stop()

    def update_title(self, title: str) -> None:
        """更新托盘图标标题。"""
        if self.icon:
            self.icon.title = title

    def show_notification(self, title: str, message: str) -> None:
        """显示系统托盘通知。"""
        if self.icon and self.is_running:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"[警告] 托盘通知显示失败: {e}")
