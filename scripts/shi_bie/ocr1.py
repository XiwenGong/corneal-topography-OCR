import sys
import os
import shutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class DropWindow(QMainWindow):
    """
    拖拽窗口类
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('拖拽文件/文件夹到这里')
        self.setGeometry(100, 100, 400, 300)
        
        # 创建中央部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建提示标签
        self.label = QLabel('将文件或文件夹拖拽到这里')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        
        # 设置接受拖拽
        self.setAcceptDrops(True)
        
        # 确保目标文件夹存在
        current_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/shi_bie
        scripts_dir = os.path.dirname(current_dir)  # scripts
        project_dir = os.path.dirname(scripts_dir)  # 项目根目录
        self.target_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')
        print(f"目标文件夹路径: {self.target_dir}")  # 调试信息
        os.makedirs(self.target_dir, exist_ok=True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        处理拖拽进入事件
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        处理拖拽放下事件
        """
        # 获取拖拽的文件/文件夹路径
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        
        # 收集所有图片文件
        image_files = []
        for path in paths:
            if os.path.isfile(path):
                # 如果是文件，检查是否为图片
                if self.is_image_file(path):
                    image_files.append(path)
            else:
                # 如果是文件夹，递归查找所有图片
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if self.is_image_file(file_path):
                            image_files.append(file_path)
        
        # 复制图片到目标文件夹
        if image_files:
            copied_files = []
            overwritten_files = []
            for image_file in image_files:
                try:
                    # 获取文件名
                    file_name = os.path.basename(image_file)
                    # 构建目标路径
                    target_path = os.path.join(self.target_dir, file_name)
                    print(f"正在复制: {image_file} -> {target_path}")  # 调试信息
                    
                    # 检查目标文件是否已存在
                    if os.path.exists(target_path):
                        overwritten_files.append(file_name)
                    
                    # 复制文件
                    shutil.copy2(image_file, target_path)
                    copied_files.append(file_name)
                except Exception as e:
                    print(f"复制文件失败: {e}")  # 调试信息
                    QMessageBox.warning(self, '错误', f'复制文件 {file_name} 失败: {str(e)}')
            
            if copied_files:
                # 构建成功消息
                success_msg = f'已成功复制 {len(copied_files)} 个图片文件到:\n{self.target_dir}'
                if overwritten_files:
                    success_msg += f'\n\n其中覆盖了 {len(overwritten_files)} 个已存在的文件:\n' + '\n'.join(overwritten_files)
                # 显示成功消息
                QMessageBox.information(self, '成功', success_msg)
                self.close()  # 拖拽成功后自动关闭窗口
            else:
                # 显示失败消息
                QMessageBox.warning(self, '失败', '没有成功复制任何文件')
        else:
            # 显示无图片消息
            QMessageBox.warning(self, '警告', '没有找到任何图片文件')

    def is_image_file(self, file_path: str) -> bool:
        """
        判断文件是否为图片
        
        @param file_path {str} 文件路径
        @return {bool} 是否为图片
        """
        # 获取文件扩展名（小写）
        ext = os.path.splitext(file_path)[1].lower()
        # 检查是否为常见图片格式
        return ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp']

def run_ocr1():
    """
    运行拖拽窗口，供主流程调用
    """
    app = QApplication(sys.argv)
    window = DropWindow()
    window.show()
    app.exec()

def main():
    """
    主函数
    """
    run_ocr1()

if __name__ == '__main__':
    main() 