# GotIt 打包说明

## 环境准备

### 安装依赖

```bash
pip install -r requirements.txt
```

## 打包方式

### 方式一：目录模式（推荐）

打包为目录形式，包含所有依赖文件，体积较大但兼容性好。

```bash
python build.py
```

输出位置: `dist/GotIt/`

### 方式二：单文件模式

打包为单个 exe 文件，首次运行解压较慢。

```bash
python build.py --single
```

输出位置: `dist/GotIt.exe`

## 构建选项

- `--no-clean`: 不清理构建目录，加快重复构建速度
- `--single`: 构建单文件版本

## 打包后文件结构

```
dist/GotIt/
├── GotIt.exe          # 主程序
├── config/
│   └── config.example.json  # 配置示例
└── models/            # OCR 模型目录（首次运行自动下载）
    └── ocr/
```

## 注意事项

1. **OCR 模型**: 打包后首次运行会自动下载 OCR 模型到用户目录
2. **配置文件**: 用户首次运行会自动生成 `config/config.json`
3. **杀毒软件**: 某些杀毒软件可能误报，需要添加信任
4. **文件签名**: 正式发布建议添加数字签名

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
