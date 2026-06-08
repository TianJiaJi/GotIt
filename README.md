# GotIt / 我懂了

> 一款优雅的桌面截图 OCR 与 AI 答题工具

GotIt（我懂了）是一款桌面截图 OCR 与 AI 答题工具。它可以框选屏幕题目，自动完成截图、文字识别和模型回答，也提供带上下文的文字对话工作区。

## 主要功能

### 截图答题
- 拖动框选截图区域，区域会在重启后保留
- 一键「截图并回答」或「仅识别文字」
- 截图时自动隐藏主窗口，避免把软件本身截进去
- 显示截图、OCR、AI 等处理阶段，阻止重复任务
- 保存最近答案，支持复制和查看 OCR 详情

### 文字对话
- 输入或读取剪贴板文本，进行连续问答
- 支持上下文记忆，可清空重置
- 快速复制 AI 回答到剪贴板

### 本地 OCR 模型
- 首次运行自动下载并管理本地 OCR 模型
- 模型存储在项目 `models/ocr/` 目录
- Windows 兼容性优化（onnxruntime 1.24.1）

### 系统集成
- 跨平台原生系统通知（Windows、macOS、Linux）
- 全局快捷键支持
- 配置修改后立即生效，无需重启软件

## 界面预览

主窗口由三个工作区组成：

1. **截图答题**：区域框选、截图答题、仅 OCR、最近结果
2. **文字对话**：输入或读取剪贴板文本，进行连续问答
3. **设置**：模型、API、截图行为、OCR 阈值、通知和快捷键

## 安装

建议使用虚拟环境：

```bash
python -m venv .venv
```

**Windows：**

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

**macOS / Linux：**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 启动

```bash
python gotit.py
```

首次启动会自动：
1. 创建 `config/config.json` 配置文件
2. 下载并设置本地 OCR 模型

也可以先复制示例配置：

```bash
cp config/config.example.json config/config.json
```

然后在软件的「设置」页填写模型、API 密钥和服务地址。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Alt + Shift + Q` | 截图并回答（组合可在设置中修改） |
| `Alt + Ctrl + 1` | 使用当前鼠标位置设置区域点 1 |
| `Alt + Ctrl + 2` | 使用当前鼠标位置设置区域点 2 |
| `Ctrl + Shift + 1` | 发送剪贴板文本给 AI，并把回答写回剪贴板 |
| `Ctrl + Shift + 0` | 清空文字对话上下文 |

> macOS 首次使用全局快捷键和截图时，可能需要授予辅助功能与屏幕录制权限。

## 输出与隐私

| 类型 | 位置 |
|------|------|
| 截图 | `outputs/screenshots/` |
| OCR 文本 | `outputs/ocr_results/` |
| 本地配置 | `config/config.json`（已被 Git 忽略） |
| OCR 模型 | `models/ocr/`（已被 Git 忽略） |
| 对话上下文 | 系统用户数据目录下的 `GotIt/clipboard_context.json` |

API 密钥、截图、识别结果和对话上下文都不应提交到仓库。

## 开发

运行内置测试：

```bash
python -m unittest discover -s tests -v
```

代码结构：

```
src/
├── config/
│   └── config.py           # 配置加载、校验和原子保存
├── core/
│   ├── workflow.py        # 截图、OCR、AI 流程编排
│   ├── screenshot.py      # 屏幕截图
│   ├── ocr.py              # OCR 识别（含本地模型支持）
│   ├── model_manager.py   # OCR 模型下载和管理
│   ├── ai_answer.py       # AI 答案生成
│   ├── llm_client.py      # LLM 客户端
│   ├── clipboard_chat.py  # 剪贴板对话
│   ├── region.py          # 截图区域管理
│   └── notifier.py        # 系统通知
├── ui/
│   └── app_ui.py           # 桌面工作台 UI
├── utils/
│   └── hotkey.py          # 全局快捷键
└── main.py                # 程序入口
```

## 技术栈

- **UI 框架**：Tkinter
- **图像处理**：Pillow
- **OCR 引擎**：RapidOCR + ONNX Runtime
- **AI 接口**：OpenAI 兼容 Chat Completions API
- **快捷键**：pynput
- **系统通知**：Windows-Toasts（Windows）、系统原生通知（macOS/Linux）

## 许可证

[Apache License 2.0](LICENSE)
