"""截图答题工具主程序。"""
import sys
import tkinter as tk
from pathlib import Path

from ui.app_ui import ModernMainWindow


def get_icon_path() -> Path:
    """获取应用图标路径。"""
    return Path(__file__).parent / "assets" / "gotit.ico"


def preinit_models():
    """预初始化：确保模型下载到项目目录。"""
    try:
        from core.model_manager import ModelManager

        model_manager = ModelManager()
        if model_manager.is_models_available():
            print("[启动] 本地模型已就绪")
        else:
            print("[启动] 首次运行，正在准备 OCR 模型...")
            model_manager.download_and_setup_models()
    except ImportError:
        # 依赖未安装，跳过模型初始化
        pass
    except Exception as e:
        print(f"[警告] 模型预加载失败: {e}")


def main():
    """创建并运行桌面应用。"""
    # 预初始化模型（在 GUI 启动前）
    preinit_models()

    # Windows DPI 感知设置，修复字体模糊问题
    if sys.platform == "win32":
        try:
            from ctypes import windll

            # 设置为 per-monitor DPI 感知模式
            # 这会告诉 Windows 不要对这个应用进行 DPI 虚拟化
            windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError, Exception):
            # 如果设置失败也没关系，继续运行
            pass

    root = tk.Tk()

    # 设置应用图标
    icon_path = get_icon_path()
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    # Windows 上禁用 DPI 缩放，让 tkinter 自己处理
    if sys.platform == "win32":
        try:
            root.tk.call('tk', 'scaling', 1.0)
        except tk.TclError:
            pass

    # 检查是否启用系统托盘
    tray_enabled = True
    tray_icon = None

    try:
        from core.tray_icon import SystemTrayIcon

        # 尝试创建系统托盘图标
        tray_icon = SystemTrayIcon(
            icon_path=icon_path,
            show_window_callback=lambda: root.after(0, _show_window),
            quit_callback=lambda: root.after(0, _quit_app),
            hide_to_tray_callback=lambda: root.after(0, _hide_to_tray),
        )

        if tray_icon.start():
            print("[启动] 系统托盘已启用")
        else:
            tray_icon = None
            print("[启动] 系统托盘不可用，将使用标准窗口模式")
    except ImportError:
        tray_icon = None
        print("[启动] pystray 未安装，系统托盘功能不可用")

    def _show_window():
        """从托盘显示窗口。"""
        if hasattr(app, 'show_from_tray'):
            app.show_from_tray()

    def _hide_to_tray():
        """隐藏到托盘。"""
        if hasattr(app, 'hide_to_tray'):
            app.hide_to_tray()

    def _quit_app():
        """退出应用程序。"""
        if hasattr(app, 'cleanup'):
            app.cleanup()
        if tray_icon:
            tray_icon.stop()
        root.destroy()

    # 使用现代化主窗口（传入托盘启用状态）
    app = ModernMainWindow(root, enable_tray=tray_icon is not None)

    # 设置托盘图标引用到应用
    if tray_icon:
        app.set_tray_icon(tray_icon)

    # 窗口关闭事件处理
    def on_closing():
        if hasattr(app, 'on_window_close'):
            app.on_window_close()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # 在单独的线程中运行托盘图标事件循环
    if tray_icon:
        import threading

        tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
        tray_thread.start()

    root.mainloop()

    # 清理托盘资源
    if tray_icon:
        tray_icon.stop()


if __name__ == "__main__":
    main()
