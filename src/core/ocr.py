"""OCR recognition and result persistence."""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any


class OCRManager:
    """Lazy RapidOCR adapter with confidence filtering."""

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

    def init_ocr(self) -> bool:
        if self.ocr is not None:
            return True
        self._initialization_attempted = True
        try:
            if self._engine_factory:
                self.ocr = self._engine_factory()
            else:
                try:
                    from rapidocr import RapidOCR
                except ImportError:
                    # Keep existing installations working during migration.
                    from rapidocr_onnxruntime import RapidOCR

                self.ocr = RapidOCR()
            print("OCR初始化成功")
            return True
        except Exception as exc:
            print(f"OCR初始化失败: {exc}")
            return False

    def _confidence_threshold(self) -> float:
        if not self.config_manager:
            return 0.5
        return float(self.config_manager.get_ocr_config().get("confidence_threshold", 0.5))

    def recognize_text(self, image_path: str | os.PathLike[str]) -> str:
        if self.ocr is None and not self.init_ocr():
            return "[OCR初始化失败]"

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
            print(f"OCR识别失败: {exc}")
            return f"[识别失败: {exc}]"

    def save_result(self, text: str, screenshot_path: str | os.PathLike[str]):
        try:
            filename = Path(screenshot_path).with_suffix(".txt").name
            txt_path = self.ocr_results_dir / filename
            txt_path.write_text(text, encoding="utf-8")
            return str(txt_path)
        except OSError as exc:
            print(f"保存OCR结果失败: {exc}")
            return None

    def is_available(self) -> bool:
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
