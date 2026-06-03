"""Windows系统通知模块"""
import sys
import threading
import time
import platform


class WindowsNotifier:
    """Windows系统通知管理器"""

    def __init__(self):
        """初始化通知管理器"""
        self.available = False
        self.app_name = "截图答题工具"
        self.toaster = None
        self.notification_counter = 0
        self.windows_version = self._get_windows_version()

        # 检查是否在Windows系统上
        if sys.platform == "win32":
            try:
                # 延迟导入，避免启动时加载慢
                from windows_toasts import WindowsToaster, AudioSource, ToastAudio
                self.WindowsToaster = WindowsToaster
                self.AudioSource = AudioSource
                self.ToastAudio = ToastAudio
                self.available = True
                print(f"系统通知功能已启用 (Windows {self.windows_version})")
            except ImportError:
                print("警告: Windows-Toasts库未安装，系统通知功能不可用")
                print("请运行: pip install Windows-Toasts")
                self.available = False
            except Exception as e:
                print(f"警告: 初始化系统通知失败: {e}")
                self.available = False
        else:
            print("警告: 系统通知仅支持Windows系统")

    def _get_windows_version(self):
        """获取Windows版本信息"""
        try:
            if platform.system() == "Windows":
                version = platform.version()
                # Windows 10: 10.0.10240+
                # Windows 11: 10.0.22000+
                if version:
                    major, minor, build = map(int, version.split('.')[:3])
                    if build >= 22000:
                        return "11"
                    elif build >= 10240:
                        return "10"
                    else:
                        return f"{major}.{minor}"
        except:
            pass
        return "Unknown"

    def is_available(self):
        """检查通知功能是否可用"""
        return self.available

    def show_answer_notification(self, answer, status='success'):
        """显示AI答题结果通知

        Args:
            answer: AI答案文本
            status: 状态（success/error）
        """
        if not self.available:
            print("系统通知功能不可用")
            return

        # 在新线程中显示通知，避免阻塞主线程
        notification_thread = threading.Thread(
            target=self._show_notification_async,
            args=(answer, status),
            daemon=True
        )
        notification_thread.start()

    def _show_notification_async(self, answer, status):
        """异步显示通知"""
        try:
            # 在当前线程中创建新的WindowsToaster实例，避免跨线程COM调用问题
            thread_toaster = self.WindowsToaster(self.app_name)

            # 根据状态设置图标和标题
            if status == 'success':
                icon = "✅"
                title = f"{icon} AI答题完成"
                # 使用默认通知音
                audio = self.ToastAudio(self.AudioSource.Default)
            else:
                icon = "❌"
                title = f"{icon} AI答题失败"
                # 使用默认通知音
                audio = self.ToastAudio(self.AudioSource.Default)

            # 限制答案长度
            display_answer = answer[:200] if len(answer) > 200 else answer
            if len(answer) > 200:
                display_answer += "..."

            # 创建唯一的通知标识符
            self.notification_counter += 1
            unique_id = f"notification_{self.notification_counter}_{int(time.time())}"

            # 创建Toast通知
            from windows_toasts import Toast
            toast = Toast()
            # 设置文本字段（第一个是标题，第二个是内容）
            toast.text_fields = [title, display_answer]
            # 设置音频
            toast.audio = audio
            # 设置唯一的tag和group来避免冲突
            toast.tag = unique_id
            toast.group = "ai_answer_group"

            # Windows 11可能需要更长的持续时间
            if self.windows_version == "11":
                # Windows 11使用标准持续时间设置
                pass
            else:
                # Windows 10兼容性设置
                pass

            # 显示通知
            thread_toaster.show_toast(toast)

        except Exception as e:
            print(f"显示系统通知失败: {e}")

    def show_ocr_notification(self, ocr_text, max_length=100):
        """显示OCR识别结果通知

        Args:
            ocr_text: OCR识别的文本
            max_length: 显示的最大文本长度
        """
        if not self.available:
            return

        # 截断过长的文本
        display_text = ocr_text[:max_length]
        if len(ocr_text) > max_length:
            display_text += "..."

        self.show_answer_notification(display_text, 'success')

    def test_notification(self):
        """测试通知功能"""
        test_messages = [
            ("这是一条测试通知，系统通知功能运行正常！", "success"),
            ("AI答题完成：答案是42", "success"),
        ]

        for message, status in test_messages:
            self.show_answer_notification(message, status)