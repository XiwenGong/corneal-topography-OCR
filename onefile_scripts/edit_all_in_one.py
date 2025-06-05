import sys
import os
import shutil
import pickle
from datetime import datetime
from typing import Any, Dict, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QSizePolicy, QPushButton, QInputDialog, QMessageBox,
    QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QComboBox
)
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QMouseEvent, QKeyEvent, QDragEnterEvent, QDropEvent
from PyQt6.QtCore import Qt, QRect, QPoint

# 颜色和类型映射
TYPE_COLORS = [QColor('#FF0000'), QColor('#00AA00'), QColor('#0000FF'), QColor('#FF9900'), QColor('#AA00AA')]
TYPE_TEXTS = ['【类型1】', '【类型2】', '【类型3】', '【类型4】', '【新类型】']
BASIC_TYPES = ['类型1', '类型2', '类型3', '类型4']
BASIC_TYPE_KEYS = ['basic_type_1', 'basic_type_2', 'basic_type_3', 'basic_type_4']
OCR_ENGINES = ['tesseractOCR', '百度OCR']

class DataManager:
    """
    数据管理器类，用于管理多个脚本的数据存储
    使用别名作为主要键，每个别名下可以存储来自不同脚本的数据
    """
    def __init__(self, pkl_file: str = None):
        """
        初始化数据管理器
        Args:
            pkl_file: pkl文件路径，如果为None则使用默认路径（mu_ban/shared_data.pkl）
        """
        if pkl_file is None:
            self.pkl_file = os.path.join(get_mu_ban_dir(), 'shared_data.pkl')
        else:
            self.pkl_file = pkl_file
        # 确保文件所在目录存在
        os.makedirs(os.path.dirname(os.path.abspath(self.pkl_file)), exist_ok=True)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """
        加载pkl文件中的数据
        Returns:
            Dict: 包含所有数据的字典
        """
        if os.path.exists(self.pkl_file):
            try:
                with open(self.pkl_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"加载数据时出错：{str(e)}")
                return {}
        else:
            # 如果文件不存在，创建一个空的数据字典并保存
            empty_data = {}
            try:
                with open(self.pkl_file, 'wb') as f:
                    pickle.dump(empty_data, f)
            except Exception as e:
                print(f"创建数据文件时出错：{str(e)}")
            return empty_data

    def has_alias(self, alias: str) -> bool:
        """
        检查别名是否已存在
        Args:
            alias: 要检查的别名
        Returns:
            bool: 别名是否存在
        """
        return alias in self.data

    def save_data(self, alias: str, script_name: str, data: dict) -> bool:
        """
        保存数据到pkl文件，内容为字典结构
        Args:
            alias: 数据别名，作为主要键
            script_name: 脚本名称，用于区分不同脚本的数据
            data: 要保存的数据（dict类型）
        Returns:
            bool: 是否保存成功
        """
        try:
            if alias not in self.data:
                self.data[alias] = {}
            save_dict = data.copy()
            save_dict['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.data[alias][script_name] = save_dict
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"保存数据时出错：{str(e)}")
            return False

    def get_data(self, alias: str, script_name: Optional[str] = None) -> Any:
        """
        获取指定别名的数据
        Args:
            alias: 数据别名
            script_name: 脚本名称，如果不提供则返回该别名下的所有数据
        Returns:
            Any: 请求的数据
        """
        if alias not in self.data:
            return None
        
        if script_name is None:
            return self.data[alias]
        
        return self.data[alias].get(script_name)

    def list_aliases(self) -> list:
        """
        列出所有已保存数据的别名
        Returns:
            list: 别名列表
        """
        return list(self.data.keys())

    def list_scripts(self, alias: str) -> list:
        """
        列出指定别名下的所有脚本名称
        Args:
            alias: 数据别名
        Returns:
            list: 脚本名称列表
        """
        if alias not in self.data:
            return []
        return list(self.data[alias].keys())

    def remove_data(self, alias: str, script_name: Optional[str] = None) -> bool:
        """
        删除指定别名的数据
        Args:
            alias: 数据别名
            script_name: 脚本名称，如果不提供则删除该别名的所有数据
        Returns:
            bool: 是否删除成功
        """
        try:
            if alias not in self.data:
                return False
            
            if script_name is None:
                del self.data[alias]
            else:
                if script_name in self.data[alias]:
                    del self.data[alias][script_name]
                else:
                    return False
            
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"删除数据时出错：{str(e)}")
            return False

    def set_global_data(self, key: str, value: any) -> bool:
        """
        设置全局（通用）数据
        Args:
            key: 全局数据的键
            value: 全局数据的值
        Returns:
            bool: 是否设置成功
        """
        try:
            if "__global__" not in self.data:
                self.data["__global__"] = {}
            self.data["__global__"][key] = value
            with open(self.pkl_file, 'wb') as f:
                pickle.dump(self.data, f)
            return True
        except Exception as e:
            print(f"设置全局数据时出错：{str(e)}")
            return False

    def get_global_data(self, key: str) -> any:
        """
        获取全局（通用）数据
        Args:
            key: 全局数据的键
        Returns:
            any: 全局数据的值
        """
        return self.data.get("__global__", {}).get(key)

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
        self.has_ended = False  # 添加标志，防止重复调用end_annotate
        self.has_new_type = False  # 添加标志，记录是否有新类型
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

    def closeEvent(self, event):
        """
        窗口关闭事件处理
        """
        if not self.has_ended:
            self.has_new_type = self.end_annotate()
        event.accept()

    def end_annotate(self):
        """
        结束标注，保存框信息到pkl
        """
        if self.has_ended:  # 如果已经结束过，直接返回
            return self.has_new_type
        self.has_ended = True  # 设置标志
        # 保存所有框信息到pkl
        box_dicts = [box.to_dict() for box in self.image_label.boxes]
        has_new_type = any(box['type'] == 5 for box in box_dicts)
        print(f"检测到新类型: {has_new_type}")
        # 保存到pkl
        self.data_manager.save_data(self.alias, 'pkl3', {'boxes': box_dicts})
        QMessageBox.information(self, '提示', f'已保存{len(box_dicts)}个框，含新类型: {has_new_type}')
        self.type_selector.close()
        self.has_new_type = has_new_type  # 保存新类型状态
        self.close()  # 自动关闭窗口
        return has_new_type

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
        temp_dir = get_lin_shi_dir()
        ext = os.path.splitext(file_path)[1]
        dest_path = os.path.join(temp_dir, f'{alias}{ext}')
        print(f"正在复制图片: {file_path} -> {dest_path}")
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

def get_project_root():
    """
    获取项目根目录
    如果是exe运行，则返回exe所在目录
    如果是脚本运行，则返回项目根目录
    """
    if getattr(sys, 'frozen', False):
        # 如果是exe运行，返回exe所在目录
        return os.path.dirname(sys.executable)
    else:
        # 如果是脚本运行，返回项目根目录
        current_dir = os.path.dirname(os.path.abspath(__file__))  # onefile_scripts
        return os.path.dirname(current_dir)  # 项目根目录

def get_mu_ban_dir():
    """
    获取mu_ban目录
    """
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    os.makedirs(mu_ban_dir, exist_ok=True)
    return mu_ban_dir

def get_lin_shi_dir():
    """
    获取lin_shi目录
    """
    lin_shi_dir = os.path.join(get_project_root(), 'lin_shi')
    os.makedirs(lin_shi_dir, exist_ok=True)
    return lin_shi_dir

def clear_temp_folder():
    """
    清空lin_shi文件夹
    """
    temp_dir = get_lin_shi_dir()
    if os.path.exists(temp_dir):
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'无法删除 {file_path}: {e}')

def get_temp_image_path(alias):
    """
    只查找lin_shi文件夹下别名+任意扩展名的图片
    """
    temp_dir = os.path.join(get_project_root(), 'lin_shi')
    if not os.path.exists(temp_dir):
        print(f"临时文件夹不存在: {temp_dir}")
        return None
    for f in os.listdir(temp_dir):
        name, ext = os.path.splitext(f)
        if name == alias:
            full_path = os.path.join(temp_dir, f)
            print(f"找到图片: {full_path}")
            return full_path
    print(f"未找到别名 {alias} 对应的图片")
    return None

def main():
    """
    主程序入口
    """
    # 获取项目根目录
    project_root = get_project_root()
    print(f"项目根目录: {project_root}")
    
    # 创建数据管理器实例，优先读取已有pkl文件
    data_manager = DataManager()  # 不指定pkl文件路径，使用默认路径
    
    # 只创建一次app
    app = QApplication(sys.argv)

    # 检查并补全基本类型
    while True:
        need_edit_basic_types = False
        for key in BASIC_TYPE_KEYS:
            if not data_manager.get_global_data(key):
                need_edit_basic_types = True
                break
        if not need_edit_basic_types:
            break
        print("需要先编辑基本类型处理方案...")
        basic_type_window = BasicTypeEditWindow(data_manager)
        basic_type_window.show()
        app.exec()
    
    # 1. 运行pkl1，获取图片别名
    window = ImageWindow(data_manager)
    window.show()
    app.exec()
    last_image_alias = window.get_saved_alias()
    print('用户保存的图片别名：', last_image_alias)

    # 2. 调用pkl2，传递图片别名
    if last_image_alias:
        # 显示类型判别方案编辑窗口
        type_scheme_window = TypeSchemeWindow(last_image_alias, data_manager)
        type_scheme_window.show()
        app.exec()

        # 3. 调用pkl3，传递图片别名
        # 读取尺寸
        data = data_manager.get_data(last_image_alias, 'image_window')
        print(f"获取到的image_window数据: {data}")
        if not data or 'size' not in data:
            print('未找到该别名下的图片尺寸')
            return
        size = data['size']
        print(f"图片尺寸: {size}")
        
        # 读取图片路径
        image_path = get_temp_image_path(last_image_alias)
        print(f"临时图片路径: {image_path}")
        if not image_path:
            print('未找到临时图片')
            return
            
        # 显示标注窗口
        print("正在创建标注窗口...")
        show_image_window = ShowImageWindow(image_path, size, last_image_alias, data_manager)
        show_image_window.show()
        app.exec()
        has_new_type = show_image_window.has_new_type
        print(f"标注完成，是否有新类型: {has_new_type}")

        # 4. 如果pkl3返回码为5，说明有新类型，调用pkl4
        if has_new_type:
            print("检测到新类型，打开OCR编辑窗口...")
            ocr_edit_window = OCREditWindow(last_image_alias, data_manager)
            ocr_edit_window.show()
            app.exec()
            print("OCR编辑窗口已关闭")
    else:
        print('未获取到图片别名，未调用pkl2、pkl3、pkl4')

    # 5. 程序结束时清空lin_shi文件夹
    clear_temp_folder()

if __name__ == '__main__':
    main()