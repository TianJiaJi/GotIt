# 配置说明

配置文件为 `config/config.json`，首次启动时自动生成。该文件可能包含 API 密钥，已在 `.gitignore` 中排除。

## 配置项

```json
{
  "app": {
    "name": "截图答题工具",
    "version": "1.1.0"
  },
  "hotkey": {
    "modifiers": "alt+shift",
    "key": "q"
  },
  "ai": {
    "model": "deepseek-v4-flash",
    "api_key": "",
    "api_base": "https://api.deepseek.com",
    "temperature": 0.3,
    "max_tokens": 400
  },
  "ocr": {
    "language": "auto",
    "confidence_threshold": 0.5
  },
  "capture": {
    "hide_window": true,
    "delay_ms": 300,
    "region": null
  },
  "display": {
    "show_result_popup": true,
    "notifications_enabled": true
  }
}
```

主要说明：

- `ai.model`：模型服务使用的模型名称。
- `ai.api_key`：模型服务 API 密钥。
- `ai.api_base`：兼容接口地址。
- `ai.temperature`：范围 `0-2`。
- `ai.max_tokens`：最大输出长度。
- `ocr.confidence_threshold`：保留 OCR 文本的最低置信度，范围 `0-1`。
- `capture.hide_window`：截图前隐藏 GotIt 主窗口。
- `capture.delay_ms`：隐藏窗口到截图之间的等待时间，范围 `0-5000`。
- `capture.region`：最近一次框选的区域坐标，由软件自动维护。
- `display.show_result_popup`：完成后是否打开详情窗口。
- `display.notifications_enabled`：是否发送系统通知。

推荐直接在软件“设置”页修改配置，保存后会立即生效。
