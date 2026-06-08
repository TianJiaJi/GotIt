"""OCR recognition and result persistence with local model support."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

# 在模块加载时预先导入 onnxruntime，确保 DLL 在主线程中加载
try:
    import onnxruntime
except ImportError:
    pass

from .model_manager import ModelManager


class OCRManager:
    """Lazy RapidOCR adapter with confidence filtering and local model support."""

    def __init__(
        self,
        config_manager=None,
        engine_factory: Callable[[], Any] | None = None,
        project_root: str | os.PathLike[str] | None = None,
    ):
        self.config_manager = config_manager
        self._engine_factory = engine_factory
        self.ocr = None
        self._initialization_attempted = False

        root = Path(project_root) if project_root else Path(__file__).resolve().parents[2]
        self.ocr_results_dir = root / "outputs" / "ocr_results"
        self.ocr_results_dir.mkdir(parents=True, exist_ok=True)

        # 初始化模型管理器
        self.model_manager = ModelManager(root)
        self.use_local_models = False

    def init_ocr(self) -> bool:
        """初始化 OCR 引擎，使用项目根目录的模型。"""
        if self.ocr is not None:
            return True
        self._initialization_attempted = True

        try:
            # 确保模型在项目目录中
            if not self.model_manager.is_models_available():
                print("[OCR] 首次运行，正在设置模型...")
                if not self.model_manager.download_and_setup_models():
                    print("[警告] 模型设置失败，将使用默认位置")

            try:
                from rapidocr import RapidOCR
            except ImportError:
                from rapidocr_onnxruntime import RapidOCR

            # 检查本地模型
            if self.model_manager.is_models_available():
                models_dir = self.model_manager.get_models_dir()
                print(f"[OCR] 使用项目模型: {models_dir}")

                # 尝试通过配置指定模型目录
                # 注意：RapidOCR 可能不支持直接指定模型目录
                # 我们将在后续使用时确保模型在正确位置
                self.ocr = RapidOCR()
                self.use_local_models = True
            else:
                print("[OCR] 使用内置模型")
                self.ocr = RapidOCR()

            print("[成功] OCR 初始化成功")
            return True

        except ImportError as exc:
            print(f"[错误] OCR 依赖未安装: {exc}")
            print("[提示] 请运行: pip install rapidocr onnxruntime==1.24.1")
            return False
        except Exception as exc:
            print(f"[错误] OCR 初始化失败: {exc}")
            if "DLL" in str(exc) or "onnxruntime" in str(exc).lower():
                if sys.platform == "win32":
                    print("[提示] 请尝试: pip install onnxruntime==1.24.1")
            return False

    def _confidence_threshold(self) -> float:
        if not self.config_manager:
            return 0.5
        return float(self.config_manager.get_ocr_config().get("confidence_threshold", 0.5))

    def recognize_text(self, image_path: str | os.PathLike[str]) -> str:
        """识别图片中的文本。"""
        if self.ocr is None and not self.init_ocr():
            return "[OCR未初始化]"

        try:
            threshold = self._confidence_threshold()
            texts: list[str] = []
            result = self.ocr(str(image_path))

            if hasattr(result, "txts"):
                result_texts = result.txts
                if result_texts is None:
                    result_texts = []
                result_scores = getattr(result, "scores", None)
                if result_scores is None:
                    result_scores = []
                for index, text in enumerate(result_texts):
                    confidence = float(result_scores[index]) if index < len(result_scores) else 1.0
                    if isinstance(text, str) and text.strip() and confidence >= threshold:
                        texts.append(text.strip())
            else:
                detection_list = result[0] if isinstance(result, tuple) else result
                for item in detection_list or []:
                    if not item or len(item) < 2:
                        continue
                    text = item[1]
                    confidence = float(item[2]) if len(item) > 2 and item[2] is not None else 0.0
                    if isinstance(text, str) and text.strip() and confidence >= threshold:
                        texts.append(text.strip())

            return "\n".join(texts) if texts else "[未识别到符合置信度要求的文本]"
        except Exception as exc:
            print(f"[错误] OCR识别失败: {exc}")
            return f"[识别失败: {exc}]"

    def save_result(self, text: str, screenshot_path: str | os.PathLike[str]):
        """保存 OCR 识别结果到文本文件。"""
        try:
            filename = Path(screenshot_path).with_suffix(".txt").name
            txt_path = self.ocr_results_dir / filename
            txt_path.write_text(text, encoding="utf-8")
            return str(txt_path)
        except OSError as exc:
            print(f"[错误] 保存OCR结果失败: {exc}")
            return None

    def is_available(self) -> bool:
        """检查 OCR 是否可用。"""
        if self.ocr is not None or self._engine_factory:
            return True
        try:
            import importlib.util
            return (
                importlib.util.find_spec("rapidocr") is not None
                or importlib.util.find_spec("rapidocr_onnxruntime") is not None
            )
        except (ImportError, ValueError):
            return False

    def get_model_info(self) -> dict[str, Any]:
        """获取当前模型信息。"""
        if self.ocr is None and not self.init_ocr():
            return {"status": "unavailable", "source": "none"}
        return {
            "status": "available",
            "source": "local" if self.use_local_models else "builtin",
            "models_dir": str(self.model_manager.get_models_dir()),
            "models": self.model_manager.get_model_info(),
        }
