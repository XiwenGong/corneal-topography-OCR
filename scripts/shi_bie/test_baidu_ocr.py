import sys
import cv2
import base64
import urllib
import requests
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QFileDialog, QHBoxLayout

class BaiduOCRTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('百度OCR测试工具')
        self.setGeometry(200, 200, 600, 500)
        layout = QVBoxLayout()

        # API Key
        self.api_key_label = QLabel('API Key:')
        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_label)
        layout.addWidget(self.api_key_input)

        # Secret Key
        self.secret_key_label = QLabel('Secret Key:')
        self.secret_key_input = QLineEdit()
        layout.addWidget(self.secret_key_label)
        layout.addWidget(self.secret_key_input)

        # 图片路径
        self.img_path_label = QLabel('图片路径:')
        img_path_layout = QHBoxLayout()
        self.img_path_input = QLineEdit()
        self.browse_btn = QPushButton('浏览')
        self.browse_btn.clicked.connect(self.browse_image)
        img_path_layout.addWidget(self.img_path_input)
        img_path_layout.addWidget(self.browse_btn)
        layout.addWidget(self.img_path_label)
        layout.addLayout(img_path_layout)

        # 识别按钮
        self.ocr_btn = QPushButton('识别')
        self.ocr_btn.clicked.connect(self.run_ocr)
        layout.addWidget(self.ocr_btn)

        # 结果显示
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)

    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, '选择图片', '', 'Images (*.png *.jpg *.jpeg *.bmp *.gif)')
        if file_path:
            self.img_path_input.setText(file_path)

    def run_ocr(self):
        api_key = self.api_key_input.text().strip()
        secret_key = self.secret_key_input.text().strip()
        img_path = self.img_path_input.text().strip()
        if not api_key or not secret_key or not img_path:
            self.result_text.setText('请填写API Key、Secret Key和图片路径！')
            return
        # 获取access_token
        token = self.get_access_token(api_key, secret_key)
        if not token:
            self.result_text.setText('获取access_token失败，请检查API Key和Secret Key！')
            return
        # 读取图片（支持中文路径）
        image = self.imread_unicode(img_path)
        if image is None:
            self.result_text.setText('图片无法读取！')
            return
        # 调用OCR
        ocr_result, api_raw = self.baidu_ocr(image, token)
        self.result_text.setText(f'API原始返回:\n{api_raw}\n\n识别结果:\n{ocr_result}')

    def get_access_token(self, api_key, secret_key):
        try:
            url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={api_key}&client_secret={secret_key}'
            resp = requests.get(url)
            data = resp.json()
            return data.get('access_token', None)
        except Exception as e:
            return None

    def get_file_content_as_base64(self, image_array, urlencoded=False):
        _, img_encoded = cv2.imencode('.png', image_array)
        content = base64.b64encode(img_encoded.tobytes()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
        return content

    def baidu_ocr(self, image_array, access_token):
        try:
            url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
            image_base64 = self.get_file_content_as_base64(image_array, True)
            payload = f'image={image_base64}&language_type=CHN_ENG&detect_direction=false&paragraph=false&probability=false&multidirectional_recognize=false'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
            result = response.json()
            api_raw = str(result)
            if "words_result" in result:
                words = result["words_result"]
                formatted_text = ""
                for word in words:
                    formatted_text += word["words"] + "\n"
                return formatted_text.strip(), api_raw
            else:
                return "", api_raw
        except Exception as e:
            return f"百度OCR识别出错: {str(e)}", ""

    def imread_unicode(self, path):
        try:
            img_array = np.fromfile(path, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            return None

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BaiduOCRTestWindow()
    window.show()
    sys.exit(app.exec()) 