"""Cross-platform desktop notifications."""

from __future__ import annotations

import platform
import shutil
import subprocess
import threading


class SystemNotifier:
    """Show native notifications without blocking the UI thread."""

    def __init__(self, app_name: str = "截图答题工具"):
        self.app_name = app_name
        self.system = platform.system()
        self._windows_types = None
        if self.system == "Windows":
            try:
                from windows_toasts import AudioSource, Toast, ToastAudio, WindowsToaster

                self._windows_types = WindowsToaster, Toast, ToastAudio, AudioSource
            except ImportError:
                self._windows_types = None

    def is_available(self) -> bool:
        if self.system == "Windows":
            return self._windows_types is not None
        if self.system == "Darwin":
            return shutil.which("osascript") is not None
        return shutil.which("notify-send") is not None

    def show_answer_notification(self, answer: str, status: str = "success") -> None:
        if not self.is_available():
            return
        thread = threading.Thread(
            target=self._show,
            args=(str(answer), status),
            daemon=True,
        )
        thread.start()

    def _show(self, answer: str, status: str) -> None:
        title = "处理完成" if status == "success" else "处理失败"
        message = answer[:240] + ("..." if len(answer) > 240 else "")
        try:
            if self.system == "Windows":
                WindowsToaster, Toast, ToastAudio, AudioSource = self._windows_types
                toaster = WindowsToaster(self.app_name)
                toast = Toast()
                toast.text_fields = [title, message]
                toast.audio = ToastAudio(AudioSource.Default)
                toaster.show_toast(toast)
            elif self.system == "Darwin":
                script = (
                    "on run argv\n"
                    "display notification (item 1 of argv) "
                    "with title (item 2 of argv) subtitle (item 3 of argv)\n"
                    "end run"
                )
                subprocess.run(
                    ["osascript", "-e", script, message, self.app_name, title],
                    check=False,
                    capture_output=True,
                    timeout=5,
                )
            else:
                subprocess.run(
                    ["notify-send", f"{self.app_name} - {title}", message],
                    check=False,
                    capture_output=True,
                    timeout=5,
                )
        except (OSError, subprocess.SubprocessError) as exc:
            print(f"显示系统通知失败: {exc}")

    def show_ocr_notification(self, ocr_text: str, max_length: int = 100) -> None:
        self.show_answer_notification(ocr_text[:max_length], "success")

    def test_notification(self) -> None:
        self.show_answer_notification("系统通知功能运行正常", "success")


# Backward-compatible import for the legacy UI.
WindowsNotifier = SystemNotifier
