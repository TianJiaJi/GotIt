import unittest

from src.core.workflow import CaptureWorkflow


class ScreenshotStub:
    def take_screenshot(self, bbox):
        return True, "/tmp/capture.png", f"区域 {bbox}", None


class OCRStub:
    def recognize_text(self, _path):
        return "1+1等于几？ A. 1 B. 2"

    def save_result(self, _text, _path):
        return "/tmp/capture.txt"


class AIStub:
    def get_answer(self, _text):
        return {"status": "success", "answer": "B. 2"}


class CaptureWorkflowTests(unittest.TestCase):
    def test_full_pipeline_reports_stages_and_result(self):
        stages = []
        workflow = CaptureWorkflow(ScreenshotStub(), OCRStub(), AIStub())

        result = workflow.run((1, 2, 3, 4), include_ai=True, on_stage=stages.append)

        self.assertTrue(result.success)
        self.assertEqual(result.answer, "B. 2")
        self.assertEqual(stages, ["capture", "ocr", "ai", "done"])

    def test_ocr_only_skips_ai(self):
        workflow = CaptureWorkflow(ScreenshotStub(), OCRStub(), AIStub())
        result = workflow.run(include_ai=False)
        self.assertTrue(result.success)
        self.assertIsNone(result.ai_result)
