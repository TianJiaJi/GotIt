# GotIt 项目说明

> GotIt（我懂了）- 桌面截图 OCR 与 AI 答题工具

## 项目概述

GotIt 是一款跨平台桌面工具，支持框选屏幕区域进行 OCR 文字识别，并通过 AI 模型生成答案。同时提供带上下文记忆的剪贴板对话功能。

## 关键设计决策

### 本地 OCR 模型管理
- OCR 模型存储在 `models/ocr/` 目录，首次运行自动下载
- 使用 `ModelManager` 类处理模型的下载、复制和状态检查
- Windows 环境使用 onnxruntime 1.24.1 以确保 DLL 兼容性

### UI 架构
- 使用 Tkinter 构建现代风格的工作台界面
- 三工作区布局：截图答题、文字对话、设置
- 深色侧边栏 + 浅色内容区的主题设计（`Theme` 类）

### 配置管理
- 配置文件位于 `config/config.json`
- 支持运行时热更新，修改后立即生效
- 使用 `ConfigManager` 类处理配置的读取、验证和保存

## 代码结构

```
src/
├── config/config.py           # 配置加载、校验和原子保存
├── core/
│   ├── workflow.py            # 截图→OCR→AI 的主要流程编排
│   ├── screenshot.py          # 跨平台屏幕截图
│   ├── ocr.py                  # OCR 识别，含本地模型支持
│   ├── model_manager.py       # OCR 模型下载和管理
│   ├── ai_answer.py           # AI 答案生成
│   ├── llm_client.py          # LLM API 客户端
│   ├── clipboard_chat.py      # 剪贴板对话与上下文管理
│   ├── region.py              # 截图区域持久化
│   └── notifier.py            # 跨平台系统通知
├── ui/app_ui.py               # 主窗口 UI（三工作区布局）
├── utils/hotkey.py            # pynput 全局快捷键
└── main.py                    # 程序入口
```

## 开发注意事项

### 添加新功能
1. UI 相关：修改 `src/ui/app_ui.py`，遵循现有的 `Theme` 风格
2. 核心逻辑：添加到 `src/core/` 下相应模块
3. 配置项：更新 `config/config.example.json` 和 `ConfigManager`

### OCR 相关
- 优先使用本地模型，通过 `ModelManager` 管理
- 如需更换模型，修改 `model_manager.py` 中的 `required_models` 列表

### AI 模型集成
- 使用 OpenAI 兼容 API，通过 `llm_client.py` 调用
- 支持自定义 API 地址和模型参数

### 测试
- 运行 `python -m unittest discover -s tests -v`
- 测试文件放在 `tests/` 目录

## 项目约定

### 中英文命名
- 项目中文名：我懂了
- 项目英文名：GotIt
- 代码注释和文档可使用中文，便于维护

### 隐私敏感
- `config/config.json` 已被 Git 忽略
- `models/ocr/` 已被 Git 忽略
- 对话上下文存储在系统用户数据目录，不提交到 Git

## 快捷键

- `Alt + Shift + Q`：截图并回答
- `Alt + Ctrl + 1/2`：设置截图区域
- `Ctrl + Shift + 1`：剪贴板 AI 问答
- `Ctrl + Shift + 0`：清空对话上下文
