"""截图答题工具主程序。"""
import tkinter as tk

from ui.app_ui import ModernMainWindow


def main():
    """创建并运行桌面应用。"""
    root = tk.Tk()

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
