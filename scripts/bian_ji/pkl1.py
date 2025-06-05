import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QSizePolicy, QPushButton, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
import os
import shutil
from datetime import datetime
from data_manager import DataManager

class ImageWindow(QMainWindow):
    """
    支持拖拽图片、图片自适应窗口、右下角实时显示图片显示尺寸的窗口
    """
    def __init__(self, data_manager: DataManager = None):
        """
        初始化窗口和UI组件
        Args:
            data_manager: 数据管理器实例，如果为None则创建新的实例
        """
        super().__init__()
        self.setWindowTitle('图片拖拽窗口')
        self.setGeometry(300, 300, 600, 400)
        self.setAcceptDrops(True)
        self.original_pixmap = None  # 原始图片
        self.saved_size = None  # 用于保存尺寸
        self.saved_alias = None  # 用于保存别名
        self.data_manager = data_manager if data_manager is not None else DataManager()  # 使用传入的数据管理器或创建新的
        self.current_image_path = None  # 记录当前图片路径

        # 图片显示标签
        self.image_label = QLabel('请拖拽图片到窗口', self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setCentralWidget(self.image_label)

        # 右下角尺寸标签
        self.size_label = QLabel(self)
        self.size_label.setStyleSheet('background: rgba(255,255,255,0.8); color: #333; border-radius: 4px; padding: 2px 8px; font-size: 12px;')
        self.size_label.hide()

        # 添加按钮
        self.save_btn = QPushButton('保存当前尺寸', self)
        self.save_btn.clicked.connect(self.save_current_size)
        self.save_btn.move(10, 10)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        处理拖入事件
        Args:
            event: 拖入事件对象
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        处理放下事件
        Args:
            event: 放下事件对象
        """
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        if files and self.is_image_file(files[0]):
            file_path = files[0]
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self.original_pixmap = pixmap
                self.current_image_path = file_path  # 记录当前图片路径
                # 以原始尺寸显示图片，并调整窗口为图片原始尺寸
                self.image_label.setPixmap(self.original_pixmap)
                self.resize(self.original_pixmap.width(), self.original_pixmap.height())
                self.update_size_label(self.original_pixmap.width(), self.original_pixmap.height())
            else:
                self.image_label.setText('图片无法加载')
                self.size_label.hide()
        else:
            self.image_label.setText('请拖拽图片到窗口')
            self.size_label.hide()
            self.original_pixmap = None

    def save_current_size(self):
        """
        弹出输入框，保存当前图片显示尺寸和别名，并关闭窗口
        """
        if self.original_pixmap:
            w = self.image_label.pixmap().width()
            h = self.image_label.pixmap().height()
            
            # 弹出输入框让用户输入别名
            alias, ok = QInputDialog.getText(self, '输入别名', '请输入当前图片的别名：')
            if ok and alias:
                # 检查别名是否已存在
                if self.data_manager.has_alias(alias):
                    # 如果别名已存在，询问用户是否覆盖
                    reply = QMessageBox.question(
                        self, 
                        '别名已存在', 
                        f'别名 "{alias}" 已存在，是否覆盖？\n覆盖将删除该别名下的所有数据。',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    
                    if reply == QMessageBox.StandardButton.No:
                        # 用户选择不覆盖，重新输入
                        self.save_current_size()
                        return
                
                self.saved_size = (w, h)
                self.saved_alias = alias
                # 保存数据到数据管理器
                data = {
                    'size': self.saved_size,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                self.data_manager.save_data(alias, 'image_window', data)
                # 复制图片到lin_shi并用别名命名
                if self.current_image_path:
                    self.copied_image_path = self.copy_to_temp(self.current_image_path, alias)
                print(f'已保存：别名={self.saved_alias}, 尺寸={self.saved_size}')
                self.close()

    def copy_to_temp(self, file_path, alias):
        """
        将图片复制到lin_shi文件夹并重命名为别名+原扩展名
        Args:
            file_path: 原图片路径
            alias: 图片别名
        Returns:
            str: 复制后的图片路径
        """
        # 获取项目根目录（scripts的上一级）
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        temp_dir = os.path.join(project_root, 'lin_shi')
        os.makedirs(temp_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1]
        dest_path = os.path.join(temp_dir, f'{alias}{ext}')
        shutil.copy(file_path, dest_path)
        return dest_path

    def resizeEvent(self, event):
        """
        重写窗口尺寸变化事件，图片自适应窗口，右下角标签实时显示图片显示尺寸
        """
        super().resizeEvent(event)
        if self.original_pixmap:
            w = self.centralWidget().width()
            h = self.centralWidget().height()
            scaled_pixmap = self.original_pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
            self.update_size_label(scaled_pixmap.width(), scaled_pixmap.height())

    def update_size_label(self, w, h):
        """
        更新右下角尺寸标签内容和位置
        Args:
            w: 当前图片显示宽度
            h: 当前图片显示高度
        """
        self.size_label.setText(f"{w} x {h}")
        self.size_label.adjustSize()
        x = self.width() - self.size_label.width() - 10
        y = self.height() - self.size_label.height() - 10
        self.size_label.move(x, y)
        self.size_label.show()

    def is_image_file(self, file_path):
        """
        判断文件是否为常见图片格式
        Args:
            file_path: 文件路径
        Returns:
            bool: 是否为图片
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']

    def get_saved_size(self):
        """
        供外部调用，获取保存的尺寸
        """
        return self.saved_size

    def get_saved_alias(self):
        """
        供外部调用，获取保存的别名
        """
        return self.saved_alias

def main():
    app = QApplication(sys.argv)
    window = ImageWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
