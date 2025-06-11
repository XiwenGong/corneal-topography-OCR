import PyInstaller.__main__
import os
import shutil

def build_view_pkl():
    """
    使用PyInstaller打包view_pkl.py为exe文件
    """
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取项目根目录
    project_root = os.path.dirname(current_dir)
    
    # 定义要打包的脚本路径
    script_path = os.path.join(project_root, 'mu_ban', 'view_pkl.py')
    
    # 定义打包参数
    params = [
        script_path,
        '--name=view_pkl',
        '--onefile',
        '--windowed',
        '--clean',
        '--noconfirm',
        f'--specpath={current_dir}',
        f'--distpath={os.path.join(project_root, "dist", "mu_ban")}',
        f'--workpath={os.path.join(project_root, "build")}',
    ]
    
    try:
        # 确保目标目录存在
        dist_mu_ban = os.path.join(project_root, 'dist', 'mu_ban')
        if not os.path.exists(dist_mu_ban):
            os.makedirs(dist_mu_ban)
            print(f"创建dist/mu_ban目录: {dist_mu_ban}")
        
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
    build_view_pkl() 