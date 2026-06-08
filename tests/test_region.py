import unittest

from src.core.region import RegionManager


class RegionManagerTests(unittest.TestCase):
    def test_bbox_is_normalized(self):
        manager = RegionManager((400, 300, 100, 50))
        self.assertEqual(manager.get_bbox(), (100, 50, 400, 300))

    def test_shortcuts_use_injected_mouse_position(self):
        manager = RegionManager(mouse_position_provider=lambda: (12, 34))
        success, _message = manager.set_point_by_shortcut(1)
        self.assertTrue(success)
        self.assertEqual(manager.point1, {"x": 12, "y": 34})
