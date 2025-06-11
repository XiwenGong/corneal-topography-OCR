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
    
    # 检查并确保mu_ban目录存在
    mu_ban_dir = os.path.join(project_root, 'mu_ban')
    if not os.path.exists(mu_ban_dir):
        os.makedirs(mu_ban_dir)
        print(f"创建mu_ban目录: {mu_ban_dir}")
    
    # 检查baidu_ocr_key.txt文件
    key_file = os.path.join(mu_ban_dir, 'baidu_ocr_key.txt')
    if not os.path.exists(key_file):
        print("警告: baidu_ocr_key.txt文件不存在！")
        print("请确保在打包前创建mu_ban/baidu_ocr_key.txt文件并填写正确的API密钥。")
        return
    
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
        
        # 检查打包后的文件
        dist_mu_ban = os.path.join(project_root, 'dist', 'mu_ban')
        if not os.path.exists(dist_mu_ban):
            os.makedirs(dist_mu_ban)
            print(f"创建dist/mu_ban目录: {dist_mu_ban}")
        
        # 复制baidu_ocr_key.txt到dist/mu_ban目录
        dist_key_file = os.path.join(dist_mu_ban, 'baidu_ocr_key.txt')
        shutil.copy2(key_file, dist_key_file)
        print(f"已复制baidu_ocr_key.txt到: {dist_key_file}")
        
    finally:
        # 清理build文件夹
        build_dir = os.path.join(project_root, "build")
        if os.path.exists(build_dir):
            print(f"正在清理build文件夹: {build_dir}")
            shutil.rmtree(build_dir)
            print("build文件夹已清理")

if __name__ == '__main__':
    build_exe()