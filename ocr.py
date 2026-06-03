"""OCR识别模块"""
import os
from rapidocr_onnxruntime import RapidOCR


class OCRManager:
    """OCR识别管理器"""

    def __init__(self):
        self.ocr = None
        self.init_ocr()

    def init_ocr(self):
        """初始化OCR引擎"""
        try:
            self.ocr = RapidOCR()
            print("OCR初始化成功")
            return True
        except Exception as e:
            print(f"OCR初始化失败: {e}")
            return False

    def recognize_text(self, image_path):
        """识别图片中的文字"""
        if self.ocr is None:
            print("OCR未初始化，无法识别")
            return None

        try:
            print(f"开始OCR识别: {image_path}")

            # RapidOCR调用：直接调用即可获取文本
            # 返回格式：([detection_list], something_else)
            # detection_list中的每个元素：[[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], text, confidence]
            result = self.ocr(image_path)

            if result is None or len(result) == 0:
                print("OCR返回空结果")
                return "[未识别到文本]"

            # RapidOCR返回tuple，第一个元素是检测结果列表
            detection_list = result[0] if isinstance(result, tuple) else result

            if detection_list is None or len(detection_list) == 0:
                print("OCR检测结果为空")
                return "[未识别到文本]"

            print(f"OCR识别到 {len(detection_list)} 个文本行")

            # 提取识别的文本
            texts = []

            # RapidOCR返回格式：[(bbox, text, confidence), ...]
            # bbox: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            # text: 识别的文本字符串
            # confidence: 置信度分数
            for item in detection_list:
                if item and len(item) >= 2:
                    # item[0] 是边界框坐标 [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]]]
                    # item[1] 是文本内容
                    # item[2] 是置信度

                    text = item[1]
                    confidence = item[2] if len(item) > 2 else 0

                    if text and isinstance(text, str) and text.strip():
                        full_text = text.strip()
                        texts.append(full_text)
                        print(f"识别到文本: '{full_text[:50]}...' (长度: {len(full_text)}, 置信度: {confidence})")

            if texts:
                recognized_text = "\n".join(texts)
                print(f"OCR识别成功，共识别到 {len(texts)} 行文本")
                print(f"识别的文本内容:\n{recognized_text}")
                return recognized_text
            else:
                print("OCR未识别到有效文本")
                return "[未识别到文本]"

        except Exception as e:
            print(f"OCR识别失败: {e}")
            import traceback
            traceback.print_exc()
            return f"[识别失败: {e}]"

    def save_result(self, text, screenshot_path):
        """保存OCR识别结果到文本文件"""
        try:
            # 生成对应的文本文件名
            txt_path = screenshot_path.replace('.png', '.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"OCR结果已保存到: {txt_path}")
            return txt_path
        except Exception as e:
            print(f"保存OCR结果失败: {e}")
            return None

    def is_available(self):
        """检查OCR是否可用"""
        return self.ocr is not None
