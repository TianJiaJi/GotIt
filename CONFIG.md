# 配置说明

## 配置文件

### 实际配置文件 (`config/config.json`)
包含你的实际配置信息（包含API密钥等敏感信息）
- **不提交到Git** - 已在 `.gitignore` 中忽略
- 本地使用 - 仅供你个人使用

### 配置示例文件 (`config/config.example.json`)  
配置模板和说明
- **提交到Git** - 可供他人参考
- 仅包含示例配置 - 无真实密钥

## 快速配置

### 1. 复制示例配置
```bash
cp config/config.example.json config/config.json
```

### 2. 修改配置文件
编辑 `config/config.json`，填入你的API密钥：

```json
{
  "ai": {
    "api_key": "your-actual-api-key-here"
  }
}
```

### 3. 启动程序
```bash
python gotit.py
```

## 配置说明

### 应用配置 (`app`)
- `name`: 应用名称
- `version`: 版本号

### 快捷键配置 (`hotkey`)
- `modifiers`: 修饰键 (alt+shift, ctrl+alt等)
- `key`: 主按键 (字母或数字)

### AI配置 (`ai`)
- `model`: 模型名称 (deepseek/deepseek-chat)
- `api_key`: API密钥
- `api_base`: API端点
- `temperature`: 温度参数 (0.1-1.0)
- `max_tokens`: 最大输出长度

### OCR配置 (`ocr`)
- `language`: 语言设置 (auto, zh, en等)
- `confidence_threshold`: 置信度阈值 (0.1-1.0)

### 显示配置 (`display`)
- `show_result_popup`: 是否显示结果弹窗 (true/false)
  - `true`: 显示详细结果对话框（包含OCR识别结果和AI答案）
  - `false`: 仅通过系统通知显示答案，不弹出详细结果

## 安全提醒

⚠️ **重要**: `config/config.json` 包含敏感信息，请勿分享或提交到Git！
