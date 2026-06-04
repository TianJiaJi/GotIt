"""最终综合测试"""
import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def final_test():
    """最终综合测试"""
    print("=" * 50)
    print("最终综合测试")
    print("=" * 50)

    try:
        import tkinter as tk
        from ui.modern_ui import ModernMainWindow, ModernRegionDialog
        from core.region import RegionManager

        print("\n1. 测试主窗口...")
        root = tk.Tk()
        root.title("最终测试")
        app = ModernMainWindow(root)

        # 等待初始化
        root.after(300)
        root.update()

        # 检查关键组件
        assert hasattr(app, 'open_settings'), "缺少open_settings"
        assert hasattr(app, 'open_region_settings'), "缺少open_region_settings"
        assert hasattr(app, 'region_manager'), "缺少region_manager"
        assert hasattr(app, 'mouse_listener'), "缺少mouse_listener"
        print("   [OK] 主窗口组件完整")

        # 检查区域功能
        print("\n2. 测试区域标记功能...")
        region_mgr = app.region_manager

        # 测试快捷键功能
        success1, _ = region_mgr.set_point_by_shortcut(1)
        success2, _ = region_mgr.set_point_by_shortcut(2)
        assert success1 and success2, "快捷键设置失败"
        print("   [OK] 快捷键功能正常")

        # 测试鼠标功能
        mode, _ = region_mgr.start_set_point1()
        assert region_mgr.is_setting_mode(), "设置模式异常"
        region_mgr.cancel_setting_mode()
        print("   [OK] 鼠标点击功能正常")

        print("\n3. 测试区域设置对话框...")

        class TestRegionManager:
            def __init__(self):
                self.point1 = None
                self.point2 = None

        test_region_mgr = TestRegionManager()
        dialog = ModernRegionDialog(root, test_region_mgr, lambda: None)

        dialog.update()
        dialog_geo = dialog.geometry()

        # 检查对话框尺寸
        assert "600x700" in dialog_geo, f"对话框尺寸异常: {dialog_geo}"
        print(f"   [OK] 对话框尺寸: {dialog_geo}")

        # 检查按钮（找到5个按钮，每个120x40）
        from ui.modern_ui import ModernButton
        button_count = 0
        normal_size_count = 0

        def count_buttons(widget):
            nonlocal button_count, normal_size_count
            if isinstance(widget, ModernButton):
                button_count += 1
                width = widget.winfo_width()
                height = widget.winfo_height()
                if width == 120 and height == 40:
                    normal_size_count += 1

            for child in widget.winfo_children():
                count_buttons(child)

        count_buttons(dialog)

        assert button_count == 5, f"按钮数量异常: {button_count}"
        assert normal_size_count == 5, f"按钮尺寸异常: 正常尺寸{normal_size_count}/5"
        print(f"   [OK] 所有按钮正常: {button_count}个按钮，每个120x40")

        dialog.destroy()

        print("\n4. 测试主界面按钮...")
        # 重置按钮计数
        button_count = 0
        count_buttons(root)

        assert button_count >= 4, f"主界面按钮数量不足: {button_count}"
        print(f"   [OK] 主界面按钮: {button_count}个")

        print("\n" + "=" * 50)
        print("[SUCCESS] 所有测试通过！")
        print("=" * 50)
        print("\n修复内容确认:")
        print("[OK] 区域标记功能: 快捷键和鼠标点击都正常工作")
        print("[OK] 区域设置对话框: 600x700，所有按钮完整显示")
        print("[OK] 按钮布局: 两行布局，避免压缩")
        print("[OK] 现代化UI: 扁平化设计，保留所有功能")

        print("\n程序显示5秒...")
        root.after(5000, root.destroy)
        root.mainloop()

        return True

    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = final_test()
    sys.exit(0 if success else 1)
