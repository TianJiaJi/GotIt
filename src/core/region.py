"""区域设置模块"""
from pynput.mouse import Controller as MouseController


class RegionManager:
    """截图区域管理器"""

    def __init__(self):
        self.capture_region = None  # 格式: (x1, y1, x2, y2)
        self.mouse_controller = MouseController()
        self.setting_point_mode = None  # 'point1' 或 'point2'

    @property
    def point1(self):
        """获取点1坐标"""
        if self.capture_region and self.capture_region[0] is not None and self.capture_region[1] is not None:
            return {'x': self.capture_region[0], 'y': self.capture_region[1]}
        return None

    @point1.setter
    def point1(self, value):
        """设置点1坐标"""
        if value is None:
            if self.capture_region:
                self.capture_region[0] = None
                self.capture_region[1] = None
        else:
            if self.capture_region is None:
                self.capture_region = [value['x'], value['y'], None, None]
            else:
                self.capture_region[0] = value['x']
                self.capture_region[1] = value['y']

    @property
    def point2(self):
        """获取点2坐标"""
        if self.capture_region and self.capture_region[2] is not None and self.capture_region[3] is not None:
            return {'x': self.capture_region[2], 'y': self.capture_region[3]}
        return None

    @point2.setter
    def point2(self, value):
        """设置点2坐标"""
        if value is None:
            if self.capture_region:
                self.capture_region[2] = None
                self.capture_region[3] = None
        else:
            if self.capture_region is None:
                self.capture_region = [None, None, value['x'], value['y']]
            else:
                self.capture_region[2] = value['x']
                self.capture_region[3] = value['y']

    def get_mouse_position(self):
        """获取当前鼠标位置"""
        return self.mouse_controller.position

    def start_set_point1(self):
        """开始设置第一个区域点"""
        self.setting_point_mode = 'point1'
        return "设置点1模式", "移动鼠标到目标位置，点击鼠标左键确认点1"

    def start_set_point2(self):
        """开始设置第二个区域点"""
        self.setting_point_mode = 'point2'
        return "设置点2模式", "移动鼠标到目标位置，点击鼠标左键确认点2"

    def record_position_by_click(self, x, y):
        """通过鼠标点击记录位置"""
        if self.setting_point_mode is None:
            return False, None

        try:
            if self.setting_point_mode == 'point1':
                if self.capture_region is None:
                    self.capture_region = [x, y, None, None]
                else:
                    self.capture_region[0] = x
                    self.capture_region[1] = y

                self.setting_point_mode = None
                return True, f"已设置点1: ({x}, {y})"

            elif self.setting_point_mode == 'point2':
                if self.capture_region is None:
                    self.capture_region = [None, None, x, y]
                else:
                    self.capture_region[2] = x
                    self.capture_region[3] = y

                self.setting_point_mode = None
                return True, f"已设置点2: ({x}, {y})"

        except Exception as e:
            print(f"设置点失败: {str(e)}")
            return False, f"设置失败: {str(e)}"

    def set_point_by_shortcut(self, point_number):
        """通过快捷键直接设置点"""
        try:
            x, y = self.get_mouse_position()

            if point_number == 1:
                if self.capture_region is None:
                    self.capture_region = [x, y, None, None]
                else:
                    self.capture_region[0] = x
                    self.capture_region[1] = y
                return True, f"已设置点1: ({x}, {y})"

            elif point_number == 2:
                if self.capture_region is None:
                    self.capture_region = [None, None, x, y]
                else:
                    self.capture_region[2] = x
                    self.capture_region[3] = y
                return True, f"已设置点2: ({x}, {y})"

        except Exception as e:
            print(f"快捷键设置点失败: {str(e)}")
            return False, f"设置失败: {str(e)}"

    def cancel_setting_mode(self):
        """取消设置模式"""
        if self.setting_point_mode is not None:
            self.setting_point_mode = None
            return True
        return False

    def clear_region(self):
        """清除截图区域设置"""
        self.capture_region = None
        self.setting_point_mode = None

    def get_region(self):
        """获取当前设置的区域"""
        return self.capture_region

    def get_region_info(self):
        """获取区域信息用于显示"""
        if self.capture_region is None:
            return "未设置", "red"

        x1, y1, x2, y2 = self.capture_region
        if x1 is not None and y1 is not None and x2 is not None and y2 is not None:
            # 计算区域的左上角和右下角
            left = min(x1, x2)
            top = min(y1, y2)
            right = max(x1, x2)
            bottom = max(y1, y2)
            width = right - left
            height = bottom - top
            return f"[OK] 区域已设置: ({left}, {top}) 大小: {width}x{height}", "green"
        elif x1 is not None and y1 is not None:
            return f"区域: 点1已设置 ({x1}, {y1})，请设置点2", "orange"
        elif x2 is not None and y2 is not None:
            return f"区域: 点2已设置 ({x2}, {y2})，请设置点1", "orange"
        else:
            return "未设置", "red"

    def is_setting_mode(self):
        """是否处于设置模式"""
        return self.setting_point_mode is not None

    def is_region_complete(self):
        """区域是否完整设置"""
        if self.capture_region is None:
            return False
        return all(coord is not None for coord in self.capture_region)

    def get_bbox(self):
        """获取截图区域的bbox"""
        if not self.is_region_complete():
            return None

        x1, y1, x2, y2 = self.capture_region
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
