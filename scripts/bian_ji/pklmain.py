import sys
import os
import subprocess
import shutil
from PyQt6.QtWidgets import QApplication
from pkl1 import ImageWindow
from data_manager import DataManager

def get_project_root():
    """
    获取项目根目录（scripts的上一级）
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def clear_temp_folder():
    """
    清空lin_shi文件夹
    """
    temp_dir = os.path.join(get_project_root(), 'lin_shi')
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

def main():
    """
    主程序入口
    """
    # 确保mu_ban文件夹存在
    mu_ban_dir = os.path.join(get_project_root(), 'mu_ban')
    os.makedirs(mu_ban_dir, exist_ok=True)
    
    # pkl文件路径（只有保存数据时才会自动创建文件）
    pkl_path = os.path.join(mu_ban_dir, 'shared_data.pkl')
    
    # 创建数据管理器实例，优先读取已有pkl文件
    data_manager = DataManager(pkl_path)
    
    # 1. 运行pkl1，获取图片别名
    app = QApplication(sys.argv)
    window = ImageWindow(data_manager)
    window.show()
    app.exec()
    last_image_alias = window.get_saved_alias()
    print('用户保存的图片别名：', last_image_alias)

    # 2. 调用pkl2，传递图片别名
    if last_image_alias:
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'pkl2.py'), last_image_alias])
        # 3. 调用pkl3，传递图片别名
        pkl3_result = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'pkl3.py'), last_image_alias])
        # 4. 如果pkl3返回码为5，说明有新类型，调用pkl4
        if pkl3_result.returncode == 5:
            subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'pkl4.py'), last_image_alias])
    else:
        print('未获取到图片别名，未调用pkl2、pkl3、pkl4')

    # 5. 程序结束时清空lin_shi文件夹
    clear_temp_folder()

if __name__ == '__main__':
    main() 