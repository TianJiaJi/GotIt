"""OCR模型管理模块，负责下载和管理本地模型。"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


class ModelManager:
    """管理 OCR 模型的下载和本地存储。"""

    def __init__(self, project_root: str | os.PathLike[str] | None = None):
        if project_root:
            self.root = Path(project_root)
        else:
            self.root = Path(__file__).resolve().parents[2]

        self.models_dir = self.root / "models" / "ocr"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # 需要的模型文件
        self.required_models = [
            "ch_PP-OCRv4_det_mobile.onnx",
            "ch_PP-OCRv4_rec_mobile.onnx",
            "ch_ppocr_mobile_v2.0_cls_mobile.onnx",
        ]

    def is_models_available(self) -> bool:
        """检查本地模型是否都存在。"""
        for model_name in self.required_models:
            if not (self.models_dir / model_name).exists():
                return False
        return True

    def get_rapidocr_models_dir(self) -> Path:
        """获取 RapidOCR 安装目录的 models 文件夹。"""
        try:
            import rapidocr
            rapidocr_path = Path(rapidocr.__file__).parent
            models_dir = rapidocr_path / "models"
            if models_dir.exists():
                return models_dir
        except (ImportError, AttributeError):
            pass

        # 备用：尝试常见的缓存位置
        if sys.platform == "win32":
            cache_base = Path(os.environ.get("LOCALAPPDATA", os.environ.get("APPDATA", ".")))
        elif sys.platform == "darwin":
            cache_base = Path.home() / ".cache"
        else:
            xdg_cache = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
            cache_base = Path(xdg_cache)

        # 检查各种可能的模型位置
        possible_dirs = [
            cache_base / "rapidocr_data",
            Path.home() / ".cache" / "rapidocr_data",
        ]

        for dir_path in possible_dirs:
            if dir_path.exists():
                for model_name in self.required_models:
                    if list(dir_path.rglob(model_name)):
                        return dir_path

        # 返回一个默认路径（可能不存在）
        return cache_base / "rapidocr_data"

    def copy_models_from_rapidocr(self) -> bool:
        """从 RapidOCR 目录复制模型到项目目录。"""
        if self.is_models_available():
            return True  # 模型已存在

        source_dir = self.get_rapidocr_models_dir()

        copied = 0
        for model_name in self.required_models:
            # 在源目录中查找模型
            source_path = None
            for candidate in source_dir.rglob(model_name):
                if candidate.is_file():
                    source_path = candidate
                    break

            if source_path and source_path.exists():
                dest_path = self.models_dir / model_name
                try:
                    shutil.copy2(source_path, dest_path)
                    size_mb = source_path.stat().st_size / (1024 * 1024)
                    print(f"[模型] 复制 {model_name} ({size_mb:.1f} MB)")
                    copied += 1
                except OSError as e:
                    print(f"[警告] 复制 {model_name} 失败: {e}")

        return copied > 0

    def download_and_setup_models(self) -> bool:
        """下载并设置模型（通过初始化 RapidOCR 触发下载）。"""
        if self.is_models_available():
            print("[模型] 本地模型已存在")
            return True

        print("[模型] 首次运行，正在初始化 OCR 模型...")

        try:
            from rapidocr import RapidOCR

            # 初始化 RapidOCR 会自动下载模型
            ocr = RapidOCR()

            # 然后复制到项目目录
            if self.copy_models_from_rapidocr():
                print(f"[完成] 模型已保存到: {self.models_dir}")
                return True
            else:
                print("[警告] 模型下载完成，但复制失败")
                return False

        except ImportError:
            print("[错误] rapidocr 未安装")
            return False
        except Exception as e:
            print(f"[错误] 模型设置失败: {e}")
            return False

    def get_models_dir(self) -> Path:
        """获取模型目录路径。"""
        return self.models_dir

    def get_model_info(self) -> dict:
        """获取模型信息。"""
        models_info = {}
        for model_name in self.required_models:
            model_path = self.models_dir / model_name
            if model_path.exists():
                models_info[model_name] = {
                    "exists": True,
                    "size_mb": model_path.stat().st_size / (1024 * 1024),
                }
            else:
                models_info[model_name] = {"exists": False, "size_mb": 0}
        return models_info
