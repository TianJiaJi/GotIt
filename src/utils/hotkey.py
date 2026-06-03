"""快捷键管理模块"""
from pynput import keyboard


class HotkeyManager:
    """快捷键管理器"""

    def __init__(self):
        self.key_states = {
            'ctrl': False,
            'alt': False,
            'shift': False
        }
        self.hotkey_config = None
        self.listener = None
        self.hotkey_callback = None  # 截图快捷键回调
        self.region_callback = None  # 区域设置快捷键回调

    def set_hotkey_config(self, config):
        """设置快捷键配置"""
        self.hotkey_config = config

    def set_hotkey_callback(self, callback):
        """设置快捷键回调函数"""
        self.hotkey_callback = callback

    def set_region_callback(self, callback):
        """设置区域设置快捷键回调函数"""
        self.region_callback = callback

    def on_key_press(self, key):
        """键盘按下事件处理"""
        try:
            # 检查修饰键
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = True
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = True
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = True
            else:
                # 检查普通按键
                char_to_check = None
                try:
                    char = key.char
                    if char:
                        char_to_check = char
                except AttributeError:
                    pass

                # 检查ESC键
                if key == keyboard.Key.esc and self.region_callback:
                    if hasattr(self.region_callback, 'on_esc_press'):
                        self.region_callback.on_esc_press()
                    return

                # 检查数字键（区域设置快捷键 ALT+CTRL+1/2）
                is_digit_key = False
                digit_value = None

                if char_to_check and char_to_check in ['1', '2']:
                    is_digit_key = True
                    digit_value = char_to_check

                if not is_digit_key and hasattr(key, 'vk'):
                    if key.vk == 49:  # 1的VK码
                        is_digit_key = True
                        digit_value = '1'
                    elif key.vk == 50:  # 2的VK码
                        is_digit_key = True
                        digit_value = '2'

                if is_digit_key and digit_value and self.region_callback:
                    if self.key_states['alt'] and self.key_states['ctrl']:
                        self.region_callback(digit_value)
                    elif hasattr(self.region_callback, 'on_digit_press_in_mode'):
                        # 如果在设置模式中按数字键
                        self.region_callback.on_digit_press_in_mode(digit_value)
                    return

                # 检查截图快捷键
                if char_to_check and self.hotkey_config:
                    if char_to_check.lower() == self.hotkey_config['key'].lower():
                        if self.check_hotkey_combination():
                            if self.hotkey_callback:
                                self.hotkey_callback()

        except Exception as e:
            print(f"键盘事件处理错误: {str(e)}")

    def on_key_release(self, key):
        """键盘释放事件处理"""
        try:
            if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                self.key_states['ctrl'] = False
            elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
                self.key_states['alt'] = False
            elif key == keyboard.Key.shift_l or key == keyboard.Key.shift_r:
                self.key_states['shift'] = False
        except AttributeError:
            pass

    def check_hotkey_combination(self):
        """检查是否满足快捷键组合条件"""
        if not self.hotkey_config:
            return False

        required_modifiers = self.hotkey_config['modifiers'].lower().split('+')

        for modifier in required_modifiers:
            if not self.key_states.get(modifier, False):
                return False

        return True

    def start_listener(self):
        """启动键盘监听器"""
        if self.listener and self.listener.is_alive():
            return

        self.listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.listener.start()

    def stop_listener(self):
        """停止键盘监听器"""
        if self.listener and self.listener.is_alive():
            self.listener.stop()

    def restart_listener(self):
        """重启键盘监听器"""
        self.stop_listener()

        # 重置按键状态
        for key in self.key_states:
            self.key_states[key] = False

        # 重新启动监听器
        self.start_listener()

    def get_key_states(self):
        """获取当前按键状态（用于UI显示）"""
        return self.key_states.copy()

    def is_modifier_pressed(self, modifier):
        """检查特定修饰键是否按下"""
        return self.key_states.get(modifier, False)
