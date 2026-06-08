"""截图功能模块"""
import os
import datetime
from PIL import ImageGrab


class ScreenshotManager:
    """截图管理器"""

    def __init__(self, project_root=None):
        if project_root is None:
            # 获取项目根目录（src目录的父目录）
            # 当前文件在src/core/screenshot.py，需要回退两级到项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.project_root = project_root
        # 设置截图保存目录
        self.screenshot_dir = os.path.join(project_root, 'outputs', 'screenshots')
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def take_screenshot(self, bbox=None):
        """截取屏幕

        Args:
            bbox: 可选，截图区域 (left, top, right, bottom)
                  如果为None，则截取整个屏幕

        Returns:
            tuple: (success: bool, filepath: str, region_text: str, error: str)
        """
        try:
            # 根据是否有bbox决定截图范围
            if bbox is not None:
                screenshot = ImageGrab.grab(bbox=bbox)
                region_text = f"区域 {bbox}"
                print(f"[成功] 使用区域截图: {bbox}")
            else:
                screenshot = ImageGrab.grab()
                region_text = "全屏"
                print("[成功] 使用全屏截图")

            # 生成文件名（使用时间戳）
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"

            # 保存到screenshots目录
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)

            print(f"[成功] 截图已保存: {filepath}")
            return True, filepath, region_text, None

        except Exception as e:
            error_msg = f"截图失败: {str(e)}"
            print(f"[错误] {error_msg}")
            return False, None, None, error_msg

    def save_screenshot(self, screenshot, filename):
        """保存截图到指定文件"""
        try:
            filepath = os.path.join(self.screenshot_dir, filename)
            screenshot.save(filepath)
            print(f"[成功] 截图已保存: {filepath}")
            return True, filepath
        except Exception as e:
            print(f"[错误] 保存截图失败: {str(e)}")
            return False, None
