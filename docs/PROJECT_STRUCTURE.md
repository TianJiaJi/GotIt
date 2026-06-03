# 项目目录结构说明

## 目录组织

```
GotIt/
├── src/                      # 源代码目录
│   ├── __init__.py          # 包初始化文件
│   ├── main.py              # 主程序入口
│   ├── config/              # 配置管理模块
│   │   ├── __init__.py
│   │   └── config.py        # 配置文件管理
│   ├── core/                # 核心功能模块
│   │   ├── __init__.py
│   │   ├── ocr.py           # OCR文字识别
│   │   ├── screenshot.py    # 截图功能
│   │   └── region.py        # 区域设置管理
│   ├── ui/                  # 用户界面模块
│   │   ├── __init__.py
│   │   └── ui.py            # GUI界面组件
│   └── utils/               # 工具模块
│       ├── __init__.py
│       └── hotkey.py        # 快捷键处理
├── tests/                   # 测试目录
│   ├── __init__.py
│   └── test_ocr.py          # OCR功能测试
├── outputs/                 # 输出文件目录
│   ├── screenshots/        # 截图文件保存位置
│   └── ocr_results/        # OCR识别结果保存位置
├── config/                  # 配置文件目录
│   └── config.ini           # 应用配置文件
├── docs/                    # 文档目录
│   └── README.md            # 详细文档
├── gotit.py                # 主入口文件（用于启动应用）
├── requirements.txt         # Python依赖列表
├── README.md              # 项目说明文档
└── .gitignore             # Git忽略文件配置
```

## 模块说明

### 核心模块 (src/core/)
- **ocr.py**: 封装RapidOCR，提供文字识别功能
- **screenshot.py**: 处理屏幕截图，支持全屏和区域截图
- **region.py**: 管理截图区域设置，支持两点定矩形区域

### 界面模块 (src/ui/)
- **ui.py**: 包含所有GUI组件和对话框

### 工具模块 (src/utils/)
- **hotkey.py**: 全局快捷键监听和处理

### 配置模块 (src/config/)
- **config.py**: 管理应用配置文件读写

## 输出文件说明

### 截图文件 (outputs/screenshots/)
- 文件命名格式: `screenshot_YYYYMMDD_HHMMSS.png`
- 自动按时间戳命名，避免覆盖

### OCR结果 (outputs/ocr_results/)
- 文件命名格式: `screenshot_YYYYMMDD_HHMMSS.txt`
- 与截图文件对应，保存识别的文本内容

## 使用说明

### 启动应用
```bash
python gotit.py
```

### 运行测试
```bash
python -m pytest tests/
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 开发规范

1. **新增功能模块**: 放入对应的src子目录（core/ui/utils/config）
2. **新增测试**: 放入tests目录，命名格式`test_*.py`
3. **新增文档**: 放入docs目录
4. **修改配置**: 编辑config/config.ini文件

## 文件路径处理

所有模块在初始化时会自动定位项目根目录，确保：
- 截图保存到 `outputs/screenshots/`
- OCR结果保存到 `outputs/ocr_results/`
- 配置文件位于 `config/config.ini`

这样无论从哪个目录启动应用，都能正确找到相关文件。