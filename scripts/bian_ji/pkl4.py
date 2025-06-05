import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QPushButton, QMessageBox
)
from data_manager import DataManager

class OCREditWindow(QMainWindow):
    def __init__(self, alias, data_manager):
        super().__init__()
        self.alias = alias
        self.data_manager = data_manager
        self.setWindowTitle(f'OCR方案编辑 - {alias}')
        self.setGeometry(300, 300, 500, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # OCR引擎下拉框
        ocr_layout = QHBoxLayout()
        ocr_label = QLabel('OCR引擎:')
        self.ocr_combo = QComboBox()
        self.ocr_combo.addItems(['tesseractOCR', '百度OCR'])
        ocr_layout.addWidget(ocr_label)
        ocr_layout.addWidget(self.ocr_combo)
        layout.addLayout(ocr_layout)

        # 预处理方案
        pre_label = QLabel('预处理方案:')
        self.pre_text = QTextEdit()
        layout.addWidget(pre_label)
        layout.addWidget(self.pre_text)

        # 后处理方案
        post_label = QLabel('后处理方案:')
        self.post_text = QTextEdit()
        layout.addWidget(post_label)
        layout.addWidget(self.post_text)

        # 保存按钮
        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.save_data)
        layout.addWidget(self.save_btn)

        # 预加载已有内容
        self.load_existing()

    def load_existing(self):
        data = self.data_manager.get_data(self.alias, 'pkl4')
        if data:
            self.ocr_combo.setCurrentText(data.get('OCR引擎', 'tesseractOCR'))
            self.pre_text.setPlainText(data.get('预处理方案', ''))
            self.post_text.setPlainText(data.get('后处理方案', ''))

    def save_data(self):
        ocr_engine = self.ocr_combo.currentText()
        pre = self.pre_text.toPlainText()
        post = self.post_text.toPlainText()
        save_dict = {
            'OCR引擎': ocr_engine,
            '预处理方案': pre,
            '后处理方案': post
        }
        self.data_manager.save_data(self.alias, 'pkl4', save_dict)
        QMessageBox.information(self, '提示', '保存成功！')
        self.close()

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('请传入图片别名作为参数')
        sys.exit(1)
    alias = sys.argv[1]
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    pkl_path = os.path.join(mu_ban_dir, 'shared_data.pkl')
    data_manager = DataManager(pkl_path)
    app = QApplication(sys.argv)
    window = OCREditWindow(alias, data_manager)
    window.show()
    sys.exit(app.exec()) 