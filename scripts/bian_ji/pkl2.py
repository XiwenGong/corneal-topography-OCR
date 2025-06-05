import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
from data_manager import DataManager

class TypeSchemeWindow(QMainWindow):
    """
    图片类型判别方案编辑窗口
    """
    def __init__(self, alias, data_manager):
        super().__init__()
        self.alias = alias
        self.data_manager = data_manager
        self.setWindowTitle(f'编辑图片类型判别方案 - {alias}')
        self.setGeometry(200, 200, 600, 400)

        # 主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 可编辑文本框
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)

        # 保存按钮
        self.save_btn = QPushButton('保存')
        self.save_btn.clicked.connect(self.save_scheme)
        layout.addWidget(self.save_btn)

        # 预加载已有内容
        self.load_existing_scheme()

    def load_existing_scheme(self):
        """
        预加载已有的判别方案
        """
        data = self.data_manager.get_data(self.alias, 'pkl2')
        if data and '图片类型判别方案' in data:
            self.text_edit.setPlainText(data['图片类型判别方案'])

    def save_scheme(self):
        """
        保存文本框内容到pkl
        """
        text = self.text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, '提示', '内容不能为空！')
            return
        # 直接保存用户输入内容，不做函数名替换
        self.data_manager.save_data(self.alias, 'pkl2', {'图片类型判别方案': text})
        QMessageBox.information(self, '提示', '保存成功！')
        self.close()

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == '__main__':
    # 示例：从命令行参数接收别名
    if len(sys.argv) < 2:
        print('请传入图片别名作为参数')
        sys.exit(1)
    alias = sys.argv[1]
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    pkl_path = os.path.join(mu_ban_dir, 'shared_data.pkl')
    data_manager = DataManager(pkl_path)
    app = QApplication(sys.argv)
    window = TypeSchemeWindow(alias, data_manager)
    window.show()
    sys.exit(app.exec()) 