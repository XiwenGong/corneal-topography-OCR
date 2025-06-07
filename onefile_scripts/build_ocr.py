import PyInstaller.__main__
import os
import shutil

def build_exe():
    """
    使用PyInstaller打包ocr_all_in_one.py为exe文件
    """
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    
    # 定义要打包的脚本路径
    script_path = os.path.join(current_dir, 'ocr_all_in_one.py')
    
    # 定义打包参数
    params = [
        script_path,
        '--name=ocr_all_in_one',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        f'--specpath={current_dir}',
        f'--distpath={os.path.join(project_root, "dist")}',
        f'--workpath={os.path.join(project_root, "build")}',
        f'--add-data={os.path.join(project_root, "mu_ban")};mu_ban',
        f'--add-data={os.path.join(project_root, "lin_shi")};lin_shi',
        f'--add-data={os.path.join(project_root, "results")};results'
    ]
    
    try:
        # 执行打包命令
        PyInstaller.__main__.run(params)
        print("打包完成！")
    finally:
        # 清理build文件夹
        build_dir = os.path.join(project_root, "build")
        if os.path.exists(build_dir):
            print(f"正在清理build文件夹: {build_dir}")
            shutil.rmtree(build_dir)
            print("build文件夹已清理")

if __name__ == '__main__':
    build_exe()