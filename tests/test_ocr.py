"""OCR测试脚本"""
from rapidocr_onnxruntime import RapidOCR
import os

# 初始化OCR
print("初始化OCR...")
ocr = RapidOCR()

# 测试图片路径（使用项目根目录下的截图）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_images = [f for f in os.listdir(project_root) if f.endswith('.png')]

if not test_images:
    print("没有找到测试图片，请先截图")
else:
    # 使用最新的截图
    test_image = test_images[-1]
    test_image_path = os.path.join(project_root, test_image)
    print(f"测试图片: {test_image}")

    # 进行OCR识别
    print("\n开始OCR识别...")
    result = ocr(test_image_path)

    print(f"\n=== OCR结果调试 ===")
    print(f"结果类型: {type(result)}")
    print(f"结果是否为None: {result is None}")
    print(f"结果长度: {len(result) if result else 0}")

    if result and len(result) > 0:
        print(f"\n前3个结果示例:")
        for i, line in enumerate(result[:3]):
            print(f"结果{i}: {line}")
            print(f"  类型: {type(line)}")
            print(f"  长度: {len(line) if isinstance(line, list) else 'N/A'}")

            # 尝试提取文本
            if isinstance(line, list) and len(line) >= 2:
                text = line[1]
                print(f"  提取的文本: '{text}'")
                print(f"  文本类型: {type(text)}")
            print()

    # 尝试提取所有文本
    print("\n=== 提取所有文本 ===")
    texts = []
    if result:
        for line in result:
            if isinstance(line, list) and len(line) >= 2:
                text = line[1]
                if text and isinstance(text, str) and text.strip():
                    texts.append(text.strip())

    print(f"识别到 {len(texts)} 行文本:")
    for i, text in enumerate(texts):
        print(f"{i+1}. {text}")
