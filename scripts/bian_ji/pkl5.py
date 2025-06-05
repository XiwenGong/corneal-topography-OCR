import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit, QPushButton, QMessageBox
)
from data_manager import DataManager

BASIC_TYPES = ['类型1', '类型2', '类型3', '类型4']
BASIC_TYPE_KEYS = ['basic_type_1', 'basic_type_2', 'basic_type_3', 'basic_type_4']
OCR_ENGINES = ['tesseractOCR', '百度OCR']

class BasicTypeEditWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setWindowTitle('基本类型框信息编辑')
        self.setGeometry(350, 350, 600, 450)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 下拉框选择类型
        type_layout = QHBoxLayout()
        type_label = QLabel('选择类型:')
        self.type_combo = QComboBox()
        self.type_combo.addItems(BASIC_TYPES)
        self.type_combo.currentIndexChanged.connect(self.load_existing)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)

        # OCR引擎下拉框
        ocr_layout = QHBoxLayout()
        ocr_label = QLabel('OCR引擎:')
        self.ocr_combo = QComboBox()
        self.ocr_combo.addItems(OCR_ENGINES)
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
        idx = self.type_combo.currentIndex()
        key = BASIC_TYPE_KEYS[idx]
        data = self.data_manager.get_global_data(key) or {}
        self.ocr_combo.setCurrentText(data.get('OCR引擎', OCR_ENGINES[0]))
        self.pre_text.setPlainText(data.get('预处理方案', ''))
        self.post_text.setPlainText(data.get('后处理方案', ''))

    def save_data(self):
        idx = self.type_combo.currentIndex()
        key = BASIC_TYPE_KEYS[idx]
        save_dict = {
            'OCR引擎': self.ocr_combo.currentText(),
            '预处理方案': self.pre_text.toPlainText(),
            '后处理方案': self.post_text.toPlainText()
        }
        self.data_manager.set_global_data(key, save_dict)
        QMessageBox.information(self, '提示', f'{BASIC_TYPES[idx]}信息已保存！')

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    pkl_path = os.path.join(mu_ban_dir, 'shared_data.pkl')
    data_manager = DataManager(pkl_path)
    app = QApplication(sys.argv)
    window = BasicTypeEditWindow(data_manager)
    window.show()
    sys.exit(app.exec()) 