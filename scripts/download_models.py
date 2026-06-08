"""下载 RapidOCR 模型到本地，方便打包使用。

运行此脚本后，模型将自动从 RapidOCR 缓存复制到 models/ocr/ 目录。
"""

import os
import shutil
import sys
from pathlib import Path


def get_rapidocr_install_dir() -> Path:
    """获取 RapidOCR 安装目录（模型下载位置）。"""
    try:
        import rapidocr
        rapidocr_path = Path(rapidocr.__file__).parent
        models_dir = rapidocr_path / "models"
        if models_dir.exists():
            return models_dir
    except (ImportError, AttributeError):
        pass

    # 如果无法从模块获取，返回默认路径
    if sys.platform == "win32":
        return Path(os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", "."))) / "rapidocr_data"
    elif sys.platform == "darwin":
        return Path.home() / ".cache" / "rapidocr_data"
    else:  # Linux
        xdg_cache = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
        return Path(xdg_cache) / "rapidocr_data"


def copy_models_to_project():
    """将 RapidOCR 模型复制到项目目录。"""
    root_dir = Path(__file__).resolve().parents[1]
    models_dir = root_dir / "models" / "ocr"
    models_dir.mkdir(parents=True, exist_ok=True)

    source_dir = get_rapidocr_install_dir()
    print(f"[信息] RapidOCR 模型目录: {source_dir}")

    # 定义需要的模型文件
    required_models = [
        "ch_PP-OCRv4_det_mobile.onnx",
        "ch_PP-OCRv4_rec_mobile.onnx",
        "ch_ppocr_mobile_v2.0_cls_mobile.onnx",
    ]

    copied = 0
    for model_name in required_models:
        source_path = source_dir / model_name
        if not source_path.exists():
            # 尝试在子目录中查找
            found = False
            for subdir in source_dir.rglob(model_name):
                if subdir.is_file():
                    source_path = subdir
                    found = True
                    break
            if not found:
                print(f"[警告] 未找到模型: {model_name}")
                continue

        dest_path = models_dir / model_name
        if not dest_path.exists() or dest_path.stat().st_size != source_path.stat().st_size:
            shutil.copy2(source_path, dest_path)
            size_mb = source_path.stat().st_size / (1024 * 1024)
            print(f"[复制] {model_name} ({size_mb:.1f} MB)")
            copied += 1
        else:
            print(f"[跳过] {model_name} (已存在)")

    return copied, models_dir


def download_and_setup():
    """下载并设置 RapidOCR 模型到项目目录。"""
    print("=" * 50)
    print("RapidOCR 模型下载工具")
    print("=" * 50)

    # 添加 src 目录到路径
    root_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root_dir / "src"))

    try:
        print("\n[步骤 1/2] 初始化 RapidOCR（首次会自动下载模型）...")
        from rapidocr import RapidOCR

        # 初始化 RapidOCR（会自动下载模型）
        ocr = RapidOCR()
        print("[成功] RapidOCR 初始化成功")

        print("\n[步骤 2/2] 复制模型到项目目录...")
        copied, models_dir = copy_models_to_project()

        print("\n" + "=" * 50)
        print(f"[完成] 模型设置完成！复制了 {copied} 个模型文件")
        print("=" * 50)
        print(f"\n模型文件位置: {models_dir}")
        print("打包时请将 models/ 目录包含在内。")

        # 列出最终模型文件
        print("\n当前模型文件:")
        for model_file in sorted(models_dir.glob("*.onnx")):
            size_mb = model_file.stat().st_size / (1024 * 1024)
            print(f"  - {model_file.name} ({size_mb:.1f} MB)")

        return True

    except ImportError:
        print("\n[错误] rapidocr 未安装")
        print("[提示] 请运行: pip install rapidocr onnxruntime==1.24.1")
        return False
    except Exception as e:
        print(f"\n[错误] 设置失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = download_and_setup()
    sys.exit(0 if success else 1)
