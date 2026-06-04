"""截图答题工具 - 主程序（现代化版本）"""
import tkinter as tk

# 导入现代化UI组件
from ui.modern_ui import ModernMainWindow


def main():
    """主函数 - 使用现代化UI"""
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