"""调试UI问题"""
import tkinter as tk
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_ui():
    """调试UI问题"""
    print("创建调试窗口...")
    root = tk.Tk()
    root.title("UI调试")
    root.geometry("500x600")
    root.resizable(False, False)

    # 设置背景色
    root.config(bg="#F9F9F9")

    print("创建头部...")
    # 头部
    header_frame = tk.Frame(root, bg="#FFFFFF", highlightbackground="#E0E0E0", highlightthickness=1)
    header_frame.pack(fill=tk.X, padx=0, pady=0)

    header_content = tk.Frame(header_frame, bg="#FFFFFF")
    header_content.pack(fill=tk.X, padx=16, pady=16)

    tk.Label(
        header_content,
        text="📸 截图答题工具",
        font=('Arial', 18, 'bold'),
        bg="#FFFFFF",
        fg="#1A1A1A"
    ).pack(side=tk.LEFT)

    print("创建主容器...")
    # 主容器
    main_container = tk.Frame(root, bg="#F9F9F9")
    main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    print("创建功能按钮卡片...")
    # 功能按钮卡片
    button_card = tk.Frame(main_container, bg="#FFFFFF", highlightbackground="#E0E0E0", highlightthickness=1)
    button_card.pack(fill=tk.X, pady=(0, 16))

    # 卡片内容
    button_content = tk.Frame(button_card, bg="#FFFFFF")
    button_content.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

    # 按钮容器
    button_row = tk.Frame(button_content, bg="#FFFFFF")
    button_row.pack(fill=tk.X)

    print("导入ModernButton...")
    from ui.modern_ui import ModernButton

    # 设置按钮
    print("创建设置按钮...")
    try:
        btn = ModernButton(
            button_row,
            text="⚙️ 设置",
            command=lambda: print("设置按钮被点击"),
            style="secondary",
            size="medium"
        )
        btn.pack(side=tk.LEFT, padx=8)
        print("设置按钮创建成功")
    except Exception as e:
        print(f"设置按钮创建失败: {e}")

    # 区域按钮
    print("创建区域按钮...")
    try:
        btn2 = ModernButton(
            button_row,
            text="🗺️ 区域",
            command=lambda: print("区域按钮被点击"),
            style="secondary",
            size="medium"
        )
        btn2.pack(side=tk.LEFT, padx=8)
        print("区域按钮创建成功")
    except Exception as e:
        print(f"区域按钮创建失败: {e}")

    # 帮助按钮
    print("创建帮助按钮...")
    try:
        btn3 = ModernButton(
            button_row,
            text="📖 帮助",
            command=lambda: print("帮助按钮被点击"),
            style="secondary",
            size="medium"
        )
        btn3.pack(side=tk.LEFT, padx=8)
        print("帮助按钮创建成功")
    except Exception as e:
        print(f"帮助按钮创建失败: {e}")

    print("所有UI组件创建完成，启动窗口...")
    root.mainloop()

if __name__ == "__main__":
    debug_ui()