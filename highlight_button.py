"""高亮显示设置按钮的位置"""
import tkinter as tk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def show_highlighted_ui():
    """显示高亮版本的UI"""
    print("创建高亮测试窗口...")
    root = tk.Tk()
    root.title("截图答题工具 - 设置按钮高亮版")
    root.geometry("500x600")
    root.resizable(False, False)

    # 设置背景色
    root.config(bg="#F9F9F9")

    # 导入现代化UI
    from ui.modern_ui import ModernMainWindow, ModernTheme, ModernButton, ModernCard

    # 创建现代化主窗口
    app = ModernMainWindow(root)

    # 在功能按钮区域添加一个醒目的提示框
    print("创建设置按钮高亮提示...")

    # 找到功能按钮卡片并添加高亮边框
    def add_highlight():
        """添加高亮提示"""
        try:
            # 创建一个高亮框架
            highlight_frame = tk.Frame(root, bg="red", bd=3)
            highlight_frame.place(x=50, y=450, width=400, height=80)

            # 添加提示文字
            hint_label = tk.Label(
                highlight_frame,
                text="👇 设置按钮在这里！👇",
                font=('Arial', 12, 'bold'),
                bg="#FFF3CD", fg="red"
            )
            hint_label.place(x=0, y=-30, width=200, height=25)

            print("高亮提示已添加，3秒后移除...")
            root.after(3000, lambda: highlight_frame.destroy())

        except Exception as e:
            print(f"添加高亮失败: {e}")

    # 延迟添加高亮，确保界面完全加载
    root.after(500, add_highlight)

    # 添加状态说明
    status_label = tk.Label(
        root,
        text="提示: 设置按钮位于窗口下半部分，在区域状态卡片下方",
        font=('Arial', 10),
        bg="#F9F9F9", fg="blue"
    )
    status_label.place(x=50, y=560, width=400, height=30)

    print("高亮窗口已启动，显示8秒...")
    root.after(8000, root.destroy)
    root.mainloop()

if __name__ == "__main__":
    show_highlighted_ui()