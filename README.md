# GotIt 截图答题工具

GotIt 是一个桌面截图 OCR 与 AI 答题工具。它可以框选屏幕题目，自动完成截图、文字识别和模型回答，也提供带上下文的文字对话工作区。

## 主要功能

- 拖动框选截图区域，区域会在重启后保留
- 一键“截图并回答”或“仅识别文字”
- 截图时自动隐藏主窗口，避免把软件本身截进去
- 显示截图、OCR、AI 等处理阶段，阻止重复任务
- 保存最近答案，支持复制和查看 OCR 详情
- 文字对话支持剪贴板读取、连续上下文和快速复制
- 配置修改后立即生效，无需重启软件
- OCR 置信度过滤
- Windows、macOS 和 Linux 原生系统通知
- 本地对话记录保存在系统用户数据目录，不再提交到 Git

## 界面

主窗口由三个工作区组成：

1. **截图答题**：区域框选、截图答题、仅 OCR、最近结果。
2. **文字对话**：输入或读取剪贴板文本，进行连续问答。
3. **设置**：模型、API、截图行为、OCR 阈值、通知和快捷键。

## 安装

建议使用虚拟环境：

```bash
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

macOS / Linux：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 启动

```bash
python gotit.py
```

首次启动会自动创建 `config/config.json`。也可以先复制示例配置：

```bash
cp config/config.example.json config/config.json
```

然后在软件的“设置”页填写模型、API 密钥和服务地址。

## 快捷键

- `Alt + Shift + Q`：截图并回答，组合可在设置中修改
- `Alt + Ctrl + 1`：使用当前鼠标位置设置区域点 1
- `Alt + Ctrl + 2`：使用当前鼠标位置设置区域点 2
- `Ctrl + Shift + 1`：发送剪贴板文本给 AI，并把回答写回剪贴板
- `Ctrl + Shift + 0`：清空文字对话上下文

macOS 首次使用全局快捷键和截图时，可能需要授予辅助功能与屏幕录制权限。

## 输出与隐私

- 截图：`outputs/screenshots/`
- OCR 文本：`outputs/ocr_results/`
- 本地配置：`config/config.json`，已被 Git 忽略
- 对话上下文：系统用户数据目录下的 `GotIt/clipboard_context.json`

API 密钥、截图、识别结果和对话上下文都不应提交到仓库。

## 开发

运行内置测试：

```bash
python -m unittest discover -s tests -v
```

代码结构：

```text
src/
├── config/config.py       # 配置加载、校验和原子保存
├── core/
│   ├── workflow.py        # 截图、OCR、AI 流程编排
│   ├── screenshot.py
│   ├── ocr.py
│   ├── ai_answer.py
│   ├── clipboard_chat.py
│   ├── region.py
│   └── notifier.py
├── ui/app_ui.py           # 当前桌面工作台
└── utils/hotkey.py
```

## 技术栈

- Tkinter
- Pillow
- RapidOCR + ONNX Runtime
- OpenAI 兼容 Chat Completions API
- pynput

## 许可证

Apache License 2.0
