import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont, QFontMetrics
from PyQt6.QtCore import Qt, QRect, QSize, pyqtSignal

class ImageWindow(QWidget):
    def __init__(self, image_paths, on_index_change, save_callback=None):
        super().__init__()
        self.setWindowTitle('图片浏览')
        self.setGeometry(100, 100, 800, 600)
        self.image_paths = image_paths
        self.index = 0
        self.on_index_change = on_index_change
        self.save_callback = save_callback

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.index_label = QLabel()
        self.index_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        self.index_label.setStyleSheet('font-size: 14px; color: #666;')

        prev_btn = QPushButton('上一张')
        next_btn = QPushButton('下一张')
        save_btn = QPushButton('保存')
        prev_btn.clicked.connect(self.prev_image)
        next_btn.clicked.connect(self.next_image)
        save_btn.clicked.connect(self.on_save_clicked)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(prev_btn)
        btn_layout.addWidget(next_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.index_label)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label, stretch=1)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.update_image()

    def update_image(self):
        img_path = self.image_paths[self.index]
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(self.image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled)
        else:
            self.image_label.setText('图片无法加载')
        self.index_label.setText(f'{self.index+1}/{len(self.image_paths)}')
        self.on_index_change(self.index, self.get_image_display_info())

    def get_image_display_info(self):
        img_path = self.image_paths[self.index]
        pixmap = QPixmap(img_path)
        label_size = self.image_label.size()
        if pixmap.isNull() or label_size.width() == 0 or label_size.height() == 0:
            return None
        img_w, img_h = pixmap.width(), pixmap.height()
        label_w, label_h = label_size.width(), label_size.height()
        scale = min(label_w / img_w, label_h / img_h)
        show_w, show_h = int(img_w * scale), int(img_h * scale)
        offset_x = (label_w - show_w) // 2
        offset_y = (label_h - show_h) // 2
        return {
            'img_w': img_w, 'img_h': img_h,
            'show_w': show_w, 'show_h': show_h,
            'offset_x': offset_x, 'offset_y': offset_y,
            'scale': scale
        }

    def resizeEvent(self, event):
        self.update_image()
        super().resizeEvent(event)

    def prev_image(self):
        if self.index > 0:
            self.index -= 1
            self.update_image()

    def next_image(self):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.update_image()

    def on_save_clicked(self):
        if self.save_callback:
            self.save_callback()

class ResultOverlayWindow(QWidget):
    save_requested = pyqtSignal(dict)  # 新增信号
    def __init__(self, image_paths, ocr_results, get_display_info_func, save_callback=None, classify_result=None):
        super().__init__()
        self.setWindowTitle('识别结果')
        self.setGeometry(950, 100, 800, 600)
        self.image_paths = image_paths
        self.ocr_results = ocr_results
        self.index = 0
        self.display_info = None
        self.get_display_info_func = get_display_info_func
        self.setMinimumSize(400, 300)
        self.setFont(QFont('Consolas', 12))
        self.setLayout(QVBoxLayout(self))
        self.save_callback = save_callback
        self.classify_result = classify_result

    def show_result(self, index, display_info):
        self.index = index
        self.display_info = display_info
        if display_info:
            self.resize(display_info['show_w'], display_info['show_h'])
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.display_info:
            return
        img_name = os.path.basename(self.image_paths[self.index])
        result = self.ocr_results.get(img_name, [])
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        if isinstance(result, list):
            for area_info in result:
                coords = area_info.get('coords')
                text = area_info.get('text', '')
                area_type = area_info.get('type')
                area_name = area_info.get('area_name')
                if coords:
                    x1, y1, x2, y2 = coords
                    # 保证左上-右下顺序
                    x1, x2 = sorted([x1, x2])
                    y1, y2 = sorted([y1, y2])
                    scale = self.display_info['scale']
                    offset_x = self.display_info['offset_x']
                    offset_y = self.display_info['offset_y']
                    rx1 = int(x1 * scale + offset_x)
                    ry1 = int(y1 * scale + offset_y)
                    rx2 = int(x2 * scale + offset_x)
                    ry2 = int(y2 * scale + offset_y)
                    rect = QRect(rx1, ry1, rx2 - rx1, ry2 - ry1)
                    print(f"[调试] 显示区: type={area_type}, area_name={area_name}, coords={coords}, rect=({rx1},{ry1},{rx2},{ry2}), text={text}")
                    painter.setPen(QColor(0, 0, 0))
                    lines = str(text).splitlines() if text else ['']
                    n_lines = len(lines)
                    if n_lines == 0:
                        continue
                    max_font_size = 32
                    area_height = max(ry2 - ry1, 1)
                    area_width = max(rx2 - rx1, 1)
                    font_size_h = int(area_height / n_lines * 0.8)
                    font_size = min(max_font_size, font_size_h)
                    font = QFont('Consolas', font_size)
                    metrics = QFontMetrics(font)
                    for try_size in range(font_size, 0, -1):
                        font.setPointSize(try_size)
                        metrics = QFontMetrics(font)
                        too_wide = False
                        for line in lines:
                            if metrics.horizontalAdvance(line) > area_width:
                                too_wide = True
                                break
                        if not too_wide:
                            font_size = try_size
                            break
                    painter.setFont(QFont('Consolas', font_size))
                    line_height = area_height / n_lines
                    for i, line in enumerate(lines):
                        line_rect = QRect(rx1, int(ry1 + i * line_height), area_width, int(line_height))
                        painter.drawText(line_rect, Qt.AlignmentFlag.AlignCenter, line)
                else:
                    print(f"[调试] 跳过显示: type={area_type}, area_name={area_name}, coords=None, text={text}")
        painter.end()

    # get_area_coords 已不再需要，所有坐标已在识别结果中

def show_image_and_results(ocr_results: dict, classify_result: dict, save_callback=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(scripts_dir)
    images_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')
    image_paths = [os.path.join(images_dir, f) for f in os.listdir(images_dir)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'))]
    image_paths.sort()
    if not image_paths:
        print('未找到图片')
        return
    app = QApplication.instance() or QApplication(sys.argv)
    result_win = None
    def on_index_change(idx, display_info):
        nonlocal result_win
        if result_win is not None:
            result_win.show_result(idx, display_info)
            if display_info:
                result_win.resize(display_info['show_w'], display_info['show_h'])
        else:
            result_win = ResultOverlayWindow(image_paths, ocr_results, None, save_callback, classify_result)
            result_win.show_result(idx, display_info)
            result_win.show()
    def save_callback_wrapper():
        if save_callback:
            save_callback(ocr_results, classify_result)
    img_win = ImageWindow(image_paths, on_index_change, save_callback=save_callback_wrapper)
    img_win.show()
    app.exec()

if __name__ == '__main__':
    # 演示用
    demo = {'img1.jpg': {'basic_type_1': 'hello\nworld', 'basic_type_2': 'foo'}, 'img2.jpg': {'error': '无识别区'}}
    show_image_and_results(demo, {}) 