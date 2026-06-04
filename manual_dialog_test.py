"""手动测试对话框组件创建"""
import sys
import os
import tkinter as tk

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def manual_dialog_test():
    """手动测试对话框创建"""
    print("手动测试对话框创建...")

    root = tk.Tk()
    root.title("手动测试")

    # 模拟region_manager
    class MockRegionManager:
        def __init__(self):
            self.point1 = None
            self.point2 = None

    try:
        print("1. 创建基础Toplevel窗口...")
        dialog = tk.Toplevel(root)
        dialog.title("区域设置")
        dialog.geometry("600x700")
        dialog.config(bg="#F9F9F9")
        print(f"   基础窗口创建成功: {dialog.geometry()}")

        print("2. 创建主容器...")
        main_container = tk.Frame(dialog, bg="#F9F9F9")
        main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)
        print(f"   主容器创建成功")

        dialog.update()
        children = dialog.winfo_children()
        print(f"   子组件数: {len(children)}")

        print("3. 创建测试按钮...")
        tk.Button(
            main_container,
            text="测试按钮",
            command=lambda: print("测试")
        ).pack(pady=10)
        print("   测试按钮创建成功")

        dialog.update()
        children = dialog.winfo_children()
        print(f"   子组件数: {len(children)}")

        for child in children:
            print(f"   - {child.__class__.__name__}: {child.winfo_geometry()}")

        print("\n手动对话框显示8秒...")
        root.after(8000, root.destroy)
        root.mainloop()

    except Exception as e:
        print(f"手动测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    manual_dialog_test()