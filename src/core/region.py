"""Screenshot region state and coordinate helpers."""

from __future__ import annotations

from collections.abc import Callable


class RegionManager:
    """Manage a rectangular capture region."""

    def __init__(
        self,
        initial_region: list[int] | tuple[int, int, int, int] | None = None,
        mouse_position_provider: Callable[[], tuple[int, int]] | None = None,
    ):
        self.capture_region = list(initial_region) if initial_region else None
        self.setting_point_mode: str | None = None
        self._mouse_position_provider = mouse_position_provider

    @property
    def point1(self):
        if self.capture_region and self.capture_region[0] is not None and self.capture_region[1] is not None:
            return {"x": self.capture_region[0], "y": self.capture_region[1]}
        return None

    @point1.setter
    def point1(self, value):
        self._set_point(0, value)

    @property
    def point2(self):
        if self.capture_region and self.capture_region[2] is not None and self.capture_region[3] is not None:
            return {"x": self.capture_region[2], "y": self.capture_region[3]}
        return None

    @point2.setter
    def point2(self, value):
        self._set_point(2, value)

    def _set_point(self, offset, value):
        if self.capture_region is None:
            self.capture_region = [None, None, None, None]
        if value is None:
            self.capture_region[offset : offset + 2] = [None, None]
        else:
            self.capture_region[offset : offset + 2] = [int(value["x"]), int(value["y"])]

    def get_mouse_position(self) -> tuple[int, int]:
        if self._mouse_position_provider:
            return self._mouse_position_provider()
        from pynput.mouse import Controller

        return tuple(int(value) for value in Controller().position)

    def start_set_point1(self):
        self.setting_point_mode = "point1"
        return "设置起点", "在屏幕上点击区域的第一个角"

    def start_set_point2(self):
        self.setting_point_mode = "point2"
        return "设置终点", "在屏幕上点击区域的对角"

    def record_position_by_click(self, x, y):
        if self.setting_point_mode is None:
            return False, "当前不在区域设置模式"
        point_number = 1 if self.setting_point_mode == "point1" else 2
        self.setting_point_mode = None
        return self.set_point(point_number, x, y)

    def set_point(self, point_number: int, x: int, y: int):
        if point_number not in (1, 2):
            return False, "区域点编号无效"
        if self.capture_region is None:
            self.capture_region = [None, None, None, None]
        offset = 0 if point_number == 1 else 2
        self.capture_region[offset : offset + 2] = [int(x), int(y)]
        return True, f"已设置点{point_number}: ({int(x)}, {int(y)})"

    def set_point_by_shortcut(self, point_number):
        try:
            x, y = self.get_mouse_position()
            return self.set_point(int(point_number), x, y)
        except Exception as exc:
            return False, f"设置失败: {exc}"

    def set_region(self, bbox: tuple[int, int, int, int] | list[int]):
        if len(bbox) != 4:
            raise ValueError("截图区域必须包含四个坐标")
        self.capture_region = [int(value) for value in bbox]

    def cancel_setting_mode(self):
        was_setting = self.setting_point_mode is not None
        self.setting_point_mode = None
        return was_setting

    def clear_region(self):
        self.capture_region = None
        self.setting_point_mode = None

    def get_region(self):
        return list(self.capture_region) if self.capture_region else None

    def get_region_info(self):
        bbox = self.get_bbox()
        if bbox:
            left, top, right, bottom = bbox
            return f"已设置 {right - left} x {bottom - top}，起点 ({left}, {top})", "green"
        if self.point1:
            return f"已设置点1 ({self.point1['x']}, {self.point1['y']})，还需点2", "orange"
        if self.point2:
            return f"已设置点2 ({self.point2['x']}, {self.point2['y']})，还需点1", "orange"
        return "未设置，将截取整个屏幕", "red"

    def is_setting_mode(self):
        return self.setting_point_mode is not None

    def is_region_complete(self):
        return bool(self.capture_region and all(value is not None for value in self.capture_region))

    def get_bbox(self):
        if not self.is_region_complete():
            return None
        x1, y1, x2, y2 = self.capture_region
        left, right = sorted((int(x1), int(x2)))
        top, bottom = sorted((int(y1), int(y2)))
        if left == right or top == bottom:
            return None
        return left, top, right, bottom
