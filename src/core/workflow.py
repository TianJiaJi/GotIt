"""Capture, OCR and AI workflow orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class CaptureResult:
    success: bool
    screenshot_path: str | None = None
    region_text: str = ""
    ocr_text: str = ""
    ocr_result_path: str | None = None
    ai_result: dict[str, str] | None = None
    error: str | None = None

    @property
    def answer(self) -> str:
        if not self.ai_result:
            return ""
        return self.ai_result.get("answer", "")


class CaptureWorkflow:
    """Run the blocking capture pipeline independently from Tkinter."""

    def __init__(self, screenshot_manager, ocr_manager, ai_manager):
        self.screenshot_manager = screenshot_manager
        self.ocr_manager = ocr_manager
        self.ai_manager = ai_manager

    def run(
        self,
        bbox=None,
        include_ai: bool = True,
        on_stage: Callable[[str], None] | None = None,
    ) -> CaptureResult:
        notify = on_stage or (lambda _stage: None)

        notify("capture")
        success, filepath, region_text, error = self.screenshot_manager.take_screenshot(bbox)
        if not success:
            return CaptureResult(False, error=error or "截图失败")

        notify("ocr")
        ocr_text = self.ocr_manager.recognize_text(filepath)
        if not ocr_text or ocr_text.startswith("["):
            return CaptureResult(
                False,
                screenshot_path=filepath,
                region_text=region_text,
                ocr_text=ocr_text or "",
                error=ocr_text or "OCR未识别到文本",
            )

        txt_path = self.ocr_manager.save_result(ocr_text, filepath)
        if not include_ai:
            notify("done")
            return CaptureResult(
                True,
                screenshot_path=filepath,
                region_text=region_text,
                ocr_text=ocr_text,
                ocr_result_path=txt_path,
            )

        notify("ai")
        ai_result = self.ai_manager.get_answer(ocr_text)
        success = ai_result.get("status") == "success"
        notify("done")
        return CaptureResult(
            success,
            screenshot_path=filepath,
            region_text=region_text,
            ocr_text=ocr_text,
            ocr_result_path=txt_path,
            ai_result=ai_result,
            error=None if success else ai_result.get("answer", "AI答题失败"),
        )
