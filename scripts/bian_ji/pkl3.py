import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QSizePolicy, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QMouseEvent, QKeyEvent
from PyQt6.QtCore import Qt, QRect, QPoint
from data_manager import DataManager

# 颜色和类型映射
TYPE_COLORS = [QColor('#FF0000'), QColor('#00AA00'), QColor('#0000FF'), QColor('#FF9900'), QColor('#AA00AA')]
TYPE_TEXTS = ['【类型1】', '【类型2】', '【类型3】', '【类型4】', '【新类型】']

class Box:
    def __init__(self, pt1, pt2, box_type=1):
        self.pt1 = pt1  # QPoint
        self.pt2 = pt2  # QPoint
        self.box_type = box_type  # 1~5

    def to_dict(self):
        return {
            'pt1': (self.pt1.x(), self.pt1.y()),
            'pt2': (self.pt2.x(), self.pt2.y()),
            'type': self.box_type
        }

class ImageLabel(QLabel):
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.boxes = []  # 已画的框
        self.current_box = None  # 正在画的框
        self.current_type = 1  # 当前类型
        self.selecting = False
        self.selected_box_idx = None  # 当前选中的框索引
        self.setMouseTracking(True)

    def set_type(self, t):
        self.current_type = t
        if self.selected_box_idx is not None:
            self.boxes[self.selected_box_idx].box_type = t
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.selecting = True
            self.current_box = None
            self.selected_box_idx = None
            self.current_type = 1  # 每次画新框时重置为类型1

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.selecting:
            self.end_point = event.position().toPoint()
            self.current_box = Box(self.start_point, self.end_point, self.current_type)
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton and self.selecting:
            self.end_point = event.position().toPoint()
            self.current_box = Box(self.start_point, self.end_point, self.current_type)
            self.boxes.append(self.current_box)
            self.selected_box_idx = len(self.boxes) - 1
            self.current_box = None
            self.selecting = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        # 画所有已画的框
        for idx, box in enumerate(self.boxes):
            pen = QPen(TYPE_COLORS[box.box_type-1], 2)
            painter.setPen(pen)
            rect = QRect(box.pt1, box.pt2)
            painter.drawRect(rect.normalized())
        # 画当前正在画的框
        if self.current_box:
            pen = QPen(TYPE_COLORS[self.current_box.box_type-1], 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            rect = QRect(self.current_box.pt1, self.current_box.pt2)
            painter.drawRect(rect.normalized())

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_C:
            self.parent().end_annotate()
        elif event.key() == Qt.Key.Key_R:
            self.boxes.clear()
            self.selected_box_idx = None
            self.update()
        elif event.key() == Qt.Key.Key_B:
            if self.boxes:
                self.boxes.pop()
                self.selected_box_idx = None
                self.update()

    def focusInEvent(self, event):
        super().focusInEvent(event)

class TypeSelector(QWidget):
    def __init__(self, image_label: ImageLabel):
        super().__init__()
        self.image_label = image_label
        self.setWindowTitle('选择类型')
        self.setGeometry(850, 200, 120, 350)
        layout = QVBoxLayout(self)
        self.buttons = []
        for i, (color, text) in enumerate(zip(TYPE_COLORS, TYPE_TEXTS)):
            btn = QPushButton(text)
            btn.setStyleSheet(f'background-color: {color.name()}; color: white; font-weight: bold; height: 50px;')
            btn.clicked.connect(lambda checked, t=i+1: self.set_type(t))
            layout.addWidget(btn)
            self.buttons.append(btn)
        layout.addStretch(1)

    def set_type(self, t):
        self.image_label.set_type(t)

class ShowImageWindow(QMainWindow):
    def __init__(self, image_path, size, alias, data_manager):
        super().__init__()
        self.setWindowTitle('图片标注')
        self.setGeometry(200, 200, size[0], size[1])
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)  # 总在最前端
        self.data_manager = data_manager
        self.alias = alias
        self.image_path = image_path
        self.size = size
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(size[0], size[1], Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label = ImageLabel(scaled_pixmap, self)
        else:
            self.image_label = QLabel('图片无法加载', self)
        self.setCentralWidget(self.image_label)
        self.type_selector = TypeSelector(self.image_label)
        self.show()
        # 计算画框窗口实际尺寸和位置，设置按钮窗口在右侧
        self.raise_()  # 确保在最前
        self.activateWindow()
        geo = self.frameGeometry()  # 用frameGeometry更准确
        btn_x = geo.x() + geo.width() + 20
        btn_y = geo.y()
        self.type_selector.move(btn_x, btn_y)
        self.type_selector.show()
        self.type_selector.raise_()
        self.type_selector.activateWindow()
        self.image_label.setFocus()
        self.image_label.parent = lambda: self  # 便于回调

    def end_annotate(self):
        # 保存所有框信息到pkl
        box_dicts = [box.to_dict() for box in self.image_label.boxes]
        has_new_type = any(box['type'] == 5 for box in box_dicts)
        # 保存到pkl
        self.data_manager.save_data(self.alias, 'pkl3', {'boxes': box_dicts})
        QMessageBox.information(self, '提示', f'已保存{len(box_dicts)}个框，含新类型: {has_new_type}')
        self.type_selector.close()
        self.close()
        # 返回是否有新类型
        sys.exit(0 if not has_new_type else 5)

def get_project_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_temp_image_path(alias):
    """
    只查找lin_shi文件夹下别名+任意扩展名的图片
    """
    temp_dir = os.path.join(get_project_root(), 'lin_shi')
    if not os.path.exists(temp_dir):
        return None
    for f in os.listdir(temp_dir):
        name, ext = os.path.splitext(f)
        if name == alias:
            return os.path.join(temp_dir, f)
    return None

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('请传入图片别名作为参数')
        sys.exit(1)
    alias = sys.argv[1]
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    pkl_path = os.path.join(mu_ban_dir, 'shared_data.pkl')
    data_manager = DataManager(pkl_path)
    # 读取尺寸
    data = data_manager.get_data(alias, 'image_window')
    if not data or 'size' not in data:
        print('未找到该别名下的图片尺寸')
        sys.exit(1)
    size = data['size']
    # 读取图片路径
    image_path = get_temp_image_path(alias)
    if not image_path:
        print('未找到临时图片')
        sys.exit(1)
    # 显示窗口
    app = QApplication(sys.argv)
    window = ShowImageWindow(image_path, size, alias, data_manager)
    window.show()
    sys.exit(app.exec()) 