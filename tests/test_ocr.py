import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from src.core.ocr import OCRManager


class StubConfig:
    def get_ocr_config(self):
        return {"confidence_threshold": 0.8}


class OCRManagerTests(unittest.TestCase):
    def test_filters_results_below_configured_confidence(self):
        detections = [
            [None, "保留这一行", 0.95],
            [None, "过滤这一行", 0.40],
        ]

        with tempfile.TemporaryDirectory() as directory:
            manager = OCRManager(
                StubConfig(),
                engine_factory=lambda: lambda _path: (detections, None),
                project_root=directory,
            )

            self.assertEqual(manager.recognize_text("question.png"), "保留这一行")

    def test_saves_result_next_to_managed_output_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = OCRManager(engine_factory=lambda: None, project_root=directory)
            path = manager.save_result("识别内容", "capture.png")

            self.assertEqual(Path(path).read_text(encoding="utf-8"), "识别内容")
            self.assertIn("outputs/ocr_results", path)

    def test_supports_current_rapidocr_output_object(self):
        result = SimpleNamespace(
            txts=["第一行", "第二行"],
            scores=[0.91, 0.2],
        )
        with tempfile.TemporaryDirectory() as directory:
            manager = OCRManager(
                StubConfig(),
                engine_factory=lambda: lambda _path: result,
                project_root=directory,
            )
            self.assertEqual(manager.recognize_text("question.png"), "第一行")
