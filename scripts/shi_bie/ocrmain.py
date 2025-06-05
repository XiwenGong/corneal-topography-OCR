from ocr1 import run_ocr1
from ocr2 import classify_with_progress
from ocr3 import recognize_with_progress
from ocr4 import show_image_and_results
from ocr6 import save_to_excel
import os
import shutil

def main():
    run_ocr1()
    classify_result = classify_with_progress()
    if not classify_result:
        print("分类失败，程序结束")
        return
    ocr_result = recognize_with_progress(classify_result)
    if not ocr_result:
        print("识别失败，程序结束")
        return

    # 保存回调，调用ocr6保存excel
    def save_callback(results, classify_result):
        print("[保存回调] 收到保存请求，正在保存到Excel...")
        save_to_excel(results, classify_result)

    show_image_and_results(ocr_result, classify_result, save_callback=save_callback)

    # 程序结束前清空临时文件夹
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(scripts_dir)
    temp_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')
    if os.path.exists(temp_dir):
        for f in os.listdir(temp_dir):
            fp = os.path.join(temp_dir, f)
            try:
                if os.path.isfile(fp) or os.path.islink(fp):
                    os.unlink(fp)
                elif os.path.isdir(fp):
                    shutil.rmtree(fp)
            except Exception as e:
                print(f'清理临时文件失败: {fp}, {e}')

if __name__ == '__main__':
    main() 