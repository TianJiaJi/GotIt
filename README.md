# 截图答题工具

智能截图OCR识别工具，支持区域截图、文字识别和AI答题功能。

## 功能特性

- 🔥 **区域截图**: 支持设置固定区域进行快速截图
- 🔑 **快捷键操作**: 全局快捷键支持，方便快捷
- 📝 **OCR识别**: 基于RapidOCR的高精度文字识别
- 🤖 **AI答题**: 集成LiteLLM调用大模型进行智能答题
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
│   │   └── region.py      # 区域管理
│   ├── ui/                # 用户界面模块
│   │   └── ui.py          # 界面组件
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
├── CONFIG.md             # 配置说明文档
├── gotit.py              # 主入口文件
├── requirements.txt       # 依赖列表
└── README.md             # 项目说明
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

- `ALT + CTRL + 1`: 设置截图区域第一个点
- `ALT + CTRL + 2`: 设置截图区域第二个点  
- `ALT + SHIFT + S`: 截图并OCR识别

### 界面操作

1. **区域设置**: 点击界面上的按钮设置截图区域
2. **截图**: 点击截图按钮或使用快捷键
3. **OCR识别**: 截图后自动进行文字识别
4. **结果保存**: 识别结果自动保存到`outputs/ocr_results`目录

## 配置说明

所有配置统一在 `config/config.json` 中管理，包括：
- 应用设置
- 快捷键配置
- AI模型配置
- OCR参数设置

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

## 注意事项

1. ⚠️ **重要**: `config/config.json` 包含API密钥，已在 `.gitignore` 中忽略，请勿分享或提交
2. 首次运行请先复制 `config.example.json` 为 `config.json` 并配置API密钥
3. 截图文件保存在`outputs/screenshots`目录
4. OCR识别结果保存在`outputs/ocr_results`目录
5. 支持中文和英文混合识别
6. AI答题遵循严格的JSON格式输出，直接显示答案

## 许可证

MIT License