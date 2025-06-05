import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QProgressBar, QTextEdit
from PyQt6.QtCore import Qt

class ProgressWindow(QWidget):
    def __init__(self, total_copy, total_judge, total_recognize):
        super().__init__()
        self.setWindowTitle('处理进度')
        self.setGeometry(400, 300, 400, 220)
        self.total_copy = total_copy
        self.total_judge = total_judge
        self.total_recognize = total_recognize
        self.copy_count = 0
        self.judge_count = 0
        self.recognize_count = 0
        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet('background:#fafafa;')
        self.text.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.text)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(max(total_copy, total_judge, total_recognize))
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)
        self.update_text()
    def update_text(self):
        lines = []
        lines.append(f'已复制: {self.copy_count} / {self.total_copy}')
        if self.copy_count >= self.total_copy:
            lines.append(f'已判断: {self.judge_count} / {self.total_judge}')
        if self.judge_count >= self.total_judge and self.total_judge > 0:
            lines.append(f'已识别: {self.recognize_count} / {self.total_recognize}')
        self.text.setText('\n'.join(lines))
    def update_copy(self, val):
        self.copy_count = val
        self.progress_bar.setMaximum(self.total_copy)
        self.progress_bar.setValue(val)
        self.update_text()
        QApplication.processEvents()
    def update_judge(self, val):
        self.judge_count = val
        self.progress_bar.setMaximum(self.total_judge)
        self.progress_bar.setValue(val)
        self.update_text()
        QApplication.processEvents()
    def update_recognize(self, val):
        self.recognize_count = val
        self.progress_bar.setMaximum(self.total_recognize)
        self.progress_bar.setValue(val)
        self.update_text()
        QApplication.processEvents()

def show_progress_window(total_copy, total_judge, total_recognize, process_func):
    """
    显示进度窗口，process_func需接收3个回调：update_copy, update_judge, update_recognize
    """
    app = QApplication.instance() or QApplication(sys.argv)
    win = ProgressWindow(total_copy, total_judge, total_recognize)
    win.show()
    def update_copy(val):
        win.update_copy(val)
    def update_judge(val):
        win.update_judge(val)
    def update_recognize(val):
        win.update_recognize(val)
    process_func(update_copy, update_judge, update_recognize)
    win.close() 