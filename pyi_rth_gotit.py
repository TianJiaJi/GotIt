"""PyInstaller runtime hook for GotIt."""

import os
import sys

# 确保 src 目录在 Python 路径中
if getattr(sys, 'frozen', False):
    # 打包后的环境
    if hasattr(sys, '_MEIPASS'):
        src_path = os.path.join(sys._MEIPASS, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
