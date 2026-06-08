"""截图答题工具主程序。"""
import sys
import tkinter as tk

from ui.app_ui import ModernMainWindow


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

    # Windows 上禁用 DPI 缩放，让 tkinter 自己处理
    if sys.platform == "win32":
        try:
            root.tk.call('tk', 'scaling', 1.0)
        except tk.TclError:
            pass

    # 使用现代化主窗口
    app = ModernMainWindow(root)

    # 窗口关闭时清理资源
    def on_closing():
        if hasattr(app, 'cleanup'):
            app.cleanup()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
