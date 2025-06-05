import os
import pickle
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

def format_data(data: dict) -> str:
    """
    美化格式化pkl数据，包括全局数据，所有键值对之间自动换行，值多行时后续行缩进
    """
    lines = []
    # 显示全局数据
    global_data = data.get("__global__", {})
    if global_data:
        lines.append("[全局数据]")
        for k, v in global_data.items():
            v_str = str(v)
            v_lines = v_str.split('\n')
            if len(v_lines) == 1:
                lines.append(f"  {k}: {v_lines[0]}")
            else:
                lines.append(f"  {k}: {v_lines[0]}")
                for l in v_lines[1:]:
                    lines.append(f"    {l}")
            lines.append("")  # 键值对后加空行
        lines.append("")  # 全局数据和别名数据之间再加空行
    # 显示别名数据
    for alias, scripts in data.items():
        if alias == "__global__":
            continue
        lines.append(f'{alias}')
        for script_name, content in scripts.items():
            lines.append(f'  {script_name}:')
            for k, v in content.items():
                if k == 'timestamp':
                    continue
                v_str = str(v)
                v_lines = v_str.split('\n')
                if len(v_lines) == 1:
                    lines.append(f'    {k}:')
                    lines.append(f'      {v_lines[0]}')
                else:
                    lines.append(f'    {k}:')
                    for l in v_lines:
                        lines.append(f'      {l}')
                lines.append("")  # 键值对后加空行
            if 'timestamp' in content:
                lines.append(f'    timestamp: {content["timestamp"]}')
                lines.append("")  # 时间戳后加空行
    return '\n'.join(lines)

class PklViewer(QMainWindow):
    """
    PKL文件查看器窗口
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PKL文件查看器')
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)  # 设置为只读
        self.text_edit.setFontFamily('Consolas')  # 使用等宽字体
        self.text_edit.setFontPointSize(10)  # 设置字体大小
        layout.addWidget(self.text_edit)

        # 加载并显示pkl文件内容
        self.load_pkl_content()

    def load_pkl_content(self):
        """
        加载并显示pkl文件内容
        """
        pkl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shared_data.pkl')
        
        if not os.path.exists(pkl_path):
            self.text_edit.setText(f"文件不存在：{pkl_path}")
            return
        
        try:
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
                content = f"=== PKL文件内容 ===\n"
                content += f"文件路径：{pkl_path}\n\n"
                content += format_data(data)
                self.text_edit.setText(content)
        except Exception as e:
            self.text_edit.setText(f"读取文件时出错：{str(e)}")

def main():
    app = QApplication(sys.argv)
    window = PklViewer()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 