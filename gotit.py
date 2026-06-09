"""截图答题工具 - 主入口文件"""
import sys
import os

# 确保 src 目录在 Python 路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')

# 开发环境
if not src_dir in sys.path:
    sys.path.insert(0, src_dir)

# 打包环境
if getattr(sys, 'frozen', False):
    if hasattr(sys, '_MEIPASS'):
        meipass_src = os.path.join(sys._MEIPASS, 'src')
        if os.path.exists(meipass_src):
            sys.path.insert(0, meipass_src)

# 导入并运行主程序
from main import main

if __name__ == "__main__":
    main()