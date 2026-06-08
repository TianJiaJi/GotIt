# OCR 模型管理

## 模型位置

GotIt 支持两种 OCR 模型使用方式：

### 1. 内置模型（默认）

RapidOCR 会自动下载模型到系统缓存目录：
- **Windows**: `%LOCALAPPDATA%\rapidocr_data`
- **macOS**: `~/.cache/rapidocr_data`
- **Linux**: `~/.cache/rapidocr_data` 或 `$XDG_CACHE_HOME/rapidocr_data`

首次运行时，模型会自动从网络下载。

### 2. 本地模型（推荐用于打包）

将模型文件放置在项目根目录的 `models/ocr/` 文件夹中：

```
GotIt/
├── models/
│   └── ocr/
│       ├── ch_PP-OCRv4_det_mobile.onnx   # 检测模型
│       ├── ch_PP-OCRv4_rec_mobile.onnx    # 识别模型
│       └── ch_ppocr_mobile_v2.0_cls_mobile.onnx  # 方向分类模型（可选）
```

使用本地模型的好处：
- 无需联网下载
- 方便打包部署
- 版本可控

## 下载模型到本地

运行以下脚本将 RapidOCR 缓存的模型复制到项目目录：

```bash
python scripts/download_models.py
```

## 依赖安装

### Windows

```bash
pip install -r requirements.txt
```

或使用安装脚本：

```bash
scripts\install.bat
```

### macOS/Linux

```bash
pip install -r requirements.txt
```

## 常见问题

### DLL 加载失败

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

## 打包部署

打包应用时，建议：

1. 使用本地模型（运行 `download_models.py`）
2. 将 `models/` 目录包含在打包文件中
3. 确保 `requirements.txt` 中的依赖在目标环境安装

模型文件大小：
- 检测模型：约 4.5 MB
- 识别模型：约 10 MB
- 方向分类模型：约 0.5 MB
