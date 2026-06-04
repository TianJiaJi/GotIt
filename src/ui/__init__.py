"""用户界面模块"""

# 导入现代化UI组件
from ui.modern_ui import (
    ModernMainWindow,
    ModernTheme,
    ModernButton,
    ModernCard,
    ModernStatusBar,
    ModernResultDialog,
    ModernRegionDialog,
    ModernSettingsDialog
)

# 保留旧版组件的兼容性导入
from ui.ui import (
    HotkeyDialog,
    OCRResultDialog,
    RegionDialog,
    SettingsDialog
)

__all__ = [
    # 现代化组件
    'ModernMainWindow',
    'ModernTheme',
    'ModernButton',
    'ModernCard',
    'ModernStatusBar',
    'ModernResultDialog',
    'ModernRegionDialog',
    'ModernSettingsDialog',
    # 兼容性组件
    'HotkeyDialog',
    'OCRResultDialog',
    'RegionDialog',
    'SettingsDialog'
]