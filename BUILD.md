# GotIt 打包说明

## 环境准备

### 安装依赖

```bash
pip install -r requirements.txt
```

## 打包方式

### 方式一：窗口化目录模式（推荐）

打包为目录形式，包含所有依赖文件。窗口化模式运行，不显示控制台窗口。

```bash
python build.py
```

输出位置: `dist/GotIt/`

**特点**：
- 无控制台窗口，用户体验更好
- 首次运行速度快（无需解压）
- 启动速度比单文件模式更快
- 文件体积较大但分发方便

### 方式二：单文件模式

打包为单个 exe 文件，窗口化模式运行。首次运行时需要解压临时文件，稍慢。

```bash
python build.py --single
```

输出位置: `dist/GotIt.exe`

**特点**：
- 单文件分发方便
- 首次运行需要解压，启动较慢
- 每次运行都会占用临时空间

## 构建选项

| 选项 | 说明 |
|------|------|
| `--no-clean` | 不清理构建目录，加快重复构建速度 |
| `--single` | 构建单文件版本 |

## 打包后文件结构

### 目录模式

```
dist/GotIt/
├── GotIt.exe                    # 主程序（窗口化运行）
├── config/
│   └── config.example.json     # 配置示例
├── src/
│   └── assets/
│       └── gotit.ico           # 系统托盘图标
└── rapidocr/
    └── models/                  # OCR 模型文件
        ├── ch_PP-OCRv4_det_mobile.onnx
        ├── ch_PP-OCRv4_rec_mobile.onnx
        └── ch_ppocr_mobile_v2.0_cls_mobile.onnx
```

### 单文件模式

```
dist/
└── GotIt.exe                    # 单文件可执行程序
```

## 系统托盘支持

打包后的程序支持系统托盘功能：

- 双击托盘图标显示/隐藏主窗口
- 右键菜单：显示窗口、隐藏到托盘、退出
- 托盘图标会随程序一起打包

## 注意事项

1. **OCR 模型**: 已打包到程序中，首次运行无需下载
2. **配置文件**: 用户首次运行会自动生成 `config/config.json`
3. **杀毒软件**: 某些杀毒软件可能误报，需要添加信任
4. **文件签名**: 正式发布建议添加数字签名
5. **Windows Defender**: SmartScreen 可能警告未知发布者

## 开发者模式打包

```bash
# 不清理构建目录（加快速度）
python build.py --no-clean
```

## 清理构建文件

```bash
# 手动清理
rm -rf build/ dist/ GotIt.spec
```

## 版本信息

当前版本：1.1.0

版本信息在 `config/config.example.json` 中维护。
