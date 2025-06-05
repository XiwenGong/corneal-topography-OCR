import os
import pickle
import importlib.util
from typing import Dict, Any, Callable
import numpy as np
import cv2
from ocr5 import show_progress_window

# 这些库会被动态执行的判别函数使用
# 如果判别函数需要其他库，可以在这里添加

def load_judge_functions(pkl_path: str) -> Dict[str, Callable]:
    """
    从pkl文件中加载所有别名的判别函数
    只查找 pkl2 下的 图片类型判别方案 字段，且函数名必须为 judge
    """
    judge_functions = {}
    try:
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        for alias in data:
            if alias == '__global__':
                continue
            func_code = None
            # 只查找 pkl2 下的 图片类型判别方案
            if 'pkl2' in data[alias] and '图片类型判别方案' in data[alias]['pkl2']:
                func_code = data[alias]['pkl2']['图片类型判别方案']
            if func_code:
                try:
                    spec = importlib.util.spec_from_loader('temp_module', loader=None)
                    module = importlib.util.module_from_spec(spec)
                    # 注入依赖
                    module.__dict__['np'] = np
                    module.__dict__['cv2'] = cv2
                    exec(func_code, module.__dict__)
                    if hasattr(module, 'judge'):
                        judge_functions[alias] = getattr(module, 'judge')
                except Exception as e:
                    print(f"加载别名 {alias} 的判别函数失败: {e}")
    except Exception as e:
        print(f"读取pkl文件失败: {e}")
    return judge_functions

def judge_images(images_dir: str, judge_functions: Dict[str, Callable]) -> Dict[str, str]:
    """
    对图片进行类型判别
    
    @param images_dir {str} 图片目录
    @param judge_functions {Dict[str, Callable]} 判别函数字典
    @return {Dict[str, str]} 图片名到类型的映射
    """
    results = {}
    
    # 遍历所有图片
    for filename in os.listdir(images_dir):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp')):
            image_path = os.path.join(images_dir, filename)
            
            # 读取图片为 np.ndarray
            image = cv2.imread(image_path)
            if image is None:
                print(f"无法读取图片: {filename}")
                results[filename] = 'unreadable'
                continue
            
            # 尝试每个判别函数
            image_type = 'unknown'
            for alias, judge_func in judge_functions.items():
                try:
                    if judge_func(image):
                        image_type = alias
                        break
                except Exception as e:
                    print(f"判别图片 {filename} 时出错: {e}")
                    continue
            
            results[filename] = image_type
            
    return results

def main() -> Dict[str, str]:
    """
    主函数
    
    @return {Dict[str, str]} 判别结果字典
    """
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/shi_bie
    scripts_dir = os.path.dirname(current_dir)  # scripts
    project_dir = os.path.dirname(scripts_dir)  # 项目根目录
    
    # 构建路径
    pkl_path = os.path.join(project_dir, 'mu_ban', 'shared_data.pkl')
    images_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')
    
    # 检查路径是否存在
    if not os.path.exists(pkl_path):
        print(f"错误: pkl文件不存在: {pkl_path}")
        return {}
    if not os.path.exists(images_dir):
        print(f"错误: 图片目录不存在: {images_dir}")
        return {}
    
    # 加载判别函数
    judge_functions = load_judge_functions(pkl_path)
    if not judge_functions:
        print("警告: 没有找到任何判别函数")
        return {}
    
    # 进行判别
    results = judge_images(images_dir, judge_functions)
    
    # 打印结果
    print("\n判别结果:")
    for filename, image_type in results.items():
        print(f"{filename}: {image_type}")
    
    return results

def classify_with_progress():
    # 统计待分类图片
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(scripts_dir)
    images_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')
    image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'))]
    total = len(image_files)
    classify_result = {}
    def process_func(update_copy, update_judge, update_recognize):
        # 复制阶段（已完成，直接更新）
        update_copy(total)
        # 判断阶段
        result = main()  # 直接调用本文件的main函数
        for i, _ in enumerate(result):
            update_judge(i+1)
        # 识别阶段跳过
        update_recognize(0)
        classify_result.update(result)
    show_progress_window(total, total, total, process_func)
    return classify_result

if __name__ == '__main__':
    main() 