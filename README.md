# 截图答题工具

智能截图OCR识别工具，支持区域截图、文字识别和AI答题功能。

## 功能特性

- 🔥 **区域截图**: 支持设置固定区域进行快速截图
- 🔑 **快捷键操作**: 全局快捷键支持，无需切换窗口
- 📝 **OCR识别**: 基于RapidOCR的高精度文字识别
- 🤖 **AI答题**: 集成LiteLLM调用大模型进行智能答题
- 💬 **剪贴板对话**: 支持剪贴板内容AI对话，保存上下文，适合连续问答
- 🔔 **系统通知**: Windows系统通知实时显示答案
- 🖥️ **显示控制**: 可控制是否显示结果弹窗，避免被打断
- 🎨 **现代化界面**: 扁平化设计，操作简单直观
- 🎯 **模块化设计**: 清晰的代码结构，易于维护

## 目录结构

```
GotIt/
├── src/                    # 源代码目录
│   ├── main.py            # 主程序
│   ├── config/            # 配置模块
│   │   └── config.py      # 配置管理
│   ├── core/              # 核心功能模块
│   │   ├── ocr.py         # OCR识别
│   │   ├── screenshot.py  # 截图功能
│   │   ├── region.py      # 区域管理
│   │   ├── ai_answer.py   # AI答题
│   │   ├── clipboard_chat.py  # 剪贴板AI对话
│   │   └── notifier.py    # 系统通知
│   ├── ui/                # 用户界面模块
│   │   ├── ui.py          # 传统UI组件
│   │   └── modern_ui.py   # 现代化UI组件
│   └── utils/             # 工具模块
│       └── hotkey.py      # 快捷键处理
├── tests/                 # 测试目录
│   └── test_ocr.py        # OCR测试
├── outputs/               # 输出目录
│   ├── screenshots/      # 截图文件
│   └── ocr_results/      # OCR结果
├── config/                # 配置目录
│   ├── config.json        # 配置文件（本地，含API密钥）
│   └── config.example.json  # 配置示例
├── README.md              # 项目说明和快速开始
├── FEATURES.md            # 完整功能文档
├── CONFIG.md              # 配置说明文档
├── gotit.py              # 主入口文件
├── requirements.txt       # 依赖列表
└── LICENSE               # 许可证
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### 快速配置

1. 复制配置示例：
   ```bash
   cp config/config.example.json config/config.json
   ```

2. 编辑 `config/config.json`，填入你的API密钥：
   ```json
   {
     "ai": {
       "api_key": "your-api-key-here"
     }
   }
   ```

详细配置说明请查看 [CONFIG.md](CONFIG.md)

### 支持的AI模型

- **DeepSeek**: `deepseek/deepseek-chat` (推荐，性价比高)
- OpenAI: `gpt-3.5-turbo`, `gpt-4`, `gpt-4o`
- Anthropic Claude: `claude-3-haiku`, `claude-3-sonnet`, `claude-3-opus`
- 其他LiteLLM支持的模型

## 使用方法

### 启动程序

```bash
python gotit.py
```

### 快捷键

- `ALT + SHIFT + Q`: 执行截图答题（默认，可配置）
- `ALT + CTRL + 1`: 设置截图区域第一个点
- `ALT + CTRL + 2`: 设置截图区域第二个点
- `CTRL + SHIFT + 1`: 剪贴板AI对话（发送剪贴板内容给AI，回答自动放回剪贴板）
- `CTRL + SHIFT + 0`: 清空对话上下文
- `ESC`: 取消设置模式

### 界面操作

1. **区域设置**: 点击界面上的按钮设置截图区域
2. **截图**: 点击截图按钮或使用快捷键
3. **OCR识别**: 截图后自动进行文字识别
4. **结果保存**: 识别结果自动保存到`outputs/ocr_results`目录
5. **显示设置**: 在设置中控制是否显示结果弹窗
6. **剪贴板对话**: 复制任何文本到剪贴板，按`CTRL+SHIFT+1`发送给AI，回答自动放回剪贴板

## 配置说明

所有配置统一在 `config/config.json` 中管理，包括：
- 应用设置
- 快捷键配置
- AI模型配置
- OCR参数设置
- 显示设置（结果弹窗控制）

详细配置说明请查看 [CONFIG.md](CONFIG.md)

## 技术栈

- **界面**: Tkinter
- **OCR**: RapidOCR + onnxruntime
- **AI答题**: LiteLLM + 大语言模型
- **快捷键**: pynput
- **图像处理**: Pillow

## 开发说明

### 运行测试

```bash
python -m pytest tests/
```

### 代码结构

- `src/config/`: 配置管理相关代码
- `src/core/`: 核心功能实现
- `src/ui/`: 用户界面组件
- `src/utils/`: 工具函数

## 文档结构

- **README.md**: 项目概述和快速开始指南
- **FEATURES.md**: 完整功能文档，包含详细的UI布局、功能模块说明
- **CONFIG.md**: 配置说明文档，包含所有配置项说明

## 注意事项

1. ⚠️ **重要**: `config/config.json` 包含API密钥，已在 `.gitignore` 中忽略，请勿分享或提交
2. 首次运行请先复制 `config.example.json` 为 `config.json` 并配置API密钥
3. 截图文件保存在`outputs/screenshots`目录
4. OCR识别结果保存在`outputs/ocr_results`目录
5. 支持中文和英文混合识别
6. AI答题遵循严格的JSON格式输出，直接显示答案
7. 剪贴板对话上下文保存在程序目录下的`clipboard_context.json`文件中

## 许可证

本项目采用 Apache License 2.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情