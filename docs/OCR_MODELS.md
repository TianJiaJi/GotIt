# OCR 模型管理

## 模型位置

GotIt 支持两种 OCR 模型使用方式：

### 1. 内置模型（默认）

RapidOCR 会自动下载模型到系统缓存目录：

| 平台 | 缓存目录 |
|------|----------|
| **Windows** | `%LOCALAPPDATA%\rapidocr_data` |
| **macOS** | `~/.cache/rapidocr_data` |
| **Linux** | `~/.cache/rapidocr_data` 或 `$XDG_CACHE_HOME/rapidocr_data` |

首次运行时，模型会自动从网络下载。

### 2. 本地模型（推荐）

将模型文件放置在项目根目录的 `models/ocr/` 文件夹中：

```
GotIt/
├── models/
│   └── ocr/
│       ├── ch_PP-OCRv4_det_mobile.onnx   # 检测模型 (~4.5 MB)
│       ├── ch_PP-OCRv4_rec_mobile.onnx    # 识别模型 (~10 MB)
│       └── ch_ppocr_mobile_v2.0_cls_mobile.onnx  # 方向分类模型 (~0.5 MB)
```

使用本地模型的好处：
- 无需联网下载
- 方便打包部署
- 版本可控
- 启动速度更快

## 自动模型下载

GotIt 1.1.0 版本开始支持自动模型下载：

1. **首次启动**：程序会检查 `models/ocr/` 目录
2. **自动下载**：如果目录为空，自动从 RapidOCR 下载模型
3. **自动复制**：将下载的模型复制到项目目录
4. **状态显示**：在 UI 中显示模型下载状态

这是通过 `src/core/model_manager.py` 中的 `ModelManager` 类实现的。

## 手动下载模型

如果你需要手动下载模型，可以：

### 方法一：运行程序自动下载

```bash
python gotit.py
```

程序会自动检测并下载缺失的模型。

### 方法二：手动下载

从以下地址下载模型文件：

- [PaddleOCR 模型下载](https://github.com/PaddlePaddle/PaddleOCR/tree/release/2.7/doc/doc_ch/models_list)

将下载的文件放到 `models/ocr/` 目录。

## 依赖安装

### Windows

```bash
pip install -r requirements.txt
```

确保 onnxruntime 版本为 1.24.1 以确保兼容性。

### macOS/Linux

```bash
pip install -r requirements.txt
```

## 常见问题

### DLL 加载失败（Windows）

如果遇到 `DLL load failed` 错误：

1. 卸载现有 onnxruntime：
   ```bash
   pip uninstall onnxruntime onnxruntime-gpu
   ```

2. 安装兼容版本：
   ```bash
   pip install onnxruntime==1.24.1
   ```

### OCR 初始化失败

1. 检查依赖是否正确安装：
   ```bash
   pip list | grep -E "rapidocr|onnxruntime"
   ```

2. 重新安装依赖：
   ```bash
   pip install rapidocr onnxruntime==1.24.1 --force-reinstall
   ```

### 模型下载失败

如果自动下载失败，请检查：
1. 网络连接是否正常
2. 防火墙是否阻止了下载
3. 尝试手动下载模型文件

## 打包部署

打包应用时，建议：

1. 运行一次程序让模型自动下载到 `models/ocr/`
2. 将 `models/` 目录包含在打包文件中
3. 确保 `requirements.txt` 中的依赖在目标环境安装

**模型文件大小**：
- 检测模型：约 4.5 MB
- 识别模型：约 10 MB
- 方向分类模型：约 0.5 MB
- **总计**：约 15 MB

## 模型版本信息

当前使用的模型版本：

| 模型类型 | 版本 | 说明 |
|----------|------|------|
| 检测模型 | ch_PP-OCRv4_det_mobile | PaddleOCR v4 轻量级检测模型 |
| 识别模型 | ch_PP-OCRv4_rec_mobile | PaddleOCR v4 轻量级识别模型 |
| 分类模型 | ch_ppocr_mobile_v2.0_cls_mobile | 文字方向分类器（可选） |
