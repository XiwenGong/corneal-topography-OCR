import os
import pickle
import importlib.util
import numpy as np
import cv2
import base64
import urllib
import requests
from ocr5 import show_progress_window
import pytesseract
from PIL import Image

# 百度OCR API的API Key和Secret Key改为从txt文件读取

def read_baidu_ocr_key():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(scripts_dir)
    key_path = os.path.join(project_dir, 'mu_ban', 'baidu_ocr_key.txt')
    api_key = ''
    secret_key = ''
    try:
        with open(key_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('API_KEY'):
                    # 解析等号右侧内容，去除引号和空格
                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                elif line.startswith('SECRET_KEY'):
                    secret_key = line.split('=', 1)[1].strip().strip('"').strip("'")
        return api_key, secret_key
    except Exception as e:
        print(f"读取百度OCR密钥文件失败: {e}")
        return '', ''

# 获取access_token

def get_access_token():
    API_KEY, SECRET_KEY = read_baidu_ocr_key()
    if not API_KEY or not SECRET_KEY:
        print("API_KEY 或 SECRET_KEY 为空，请在 mu_ban/baidu_ocr_key.txt 中填写！")
        return None
    try:
        url = f'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}'
        resp = requests.get(url)
        data = resp.json()
        return data.get('access_token', None)
    except Exception as e:
        print(f"获取access_token失败: {e}")
        return None

def get_file_content_as_base64(image_array, urlencoded=False):
    _, img_encoded = cv2.imencode('.png', image_array)
    content = base64.b64encode(img_encoded.tobytes()).decode("utf8")
    if urlencoded:
        content = urllib.parse.quote_plus(content)
    return content

def baidu_ocr(image_array, access_token):
    try:
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
        image_base64 = get_file_content_as_base64(image_array, True)
        payload = f'image={image_base64}&language_type=CHN_ENG&detect_direction=false&paragraph=false&probability=false&multidirectional_recognize=false'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload.encode("utf-8"))
        result = response.json()
        if "words_result" in result:
            words = result["words_result"]
            formatted_text = ""
            for word in words:
                formatted_text += word["words"] + "\n"
            return formatted_text.strip()
        else:
            return ""
    except Exception as e:
        print(f"百度OCR识别出错: {str(e)}")
        return ""

def tesseract_ocr(image_array, access_token=None):
    # image_array: numpy.ndarray (BGR)
    try:
        # 转为RGB
        rgb_img = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')
        return text.strip()
    except Exception as e:
        print(f"Tesseract OCR识别出错: {e}")
        return ""

OCR_ENGINES = {
    'tesseractOCR': tesseract_ocr,
    '百度OCR': baidu_ocr
}

def load_recognition_schemes(pkl_path):
    """
    读取shared_data.pkl，获取每个类别的识别区划分方案、预处理、后处理、OCR引擎
    返回：
      schemes: {类别: {区名: {pre, post, ocr_engine, 区域坐标}}}
      global_basic_types: {basic_type_x: {...}}
    """
    with open(pkl_path, 'rb') as f:
        data = pickle.load(f)
    schemes = {}
    global_basic_types = {}
    for alias in data:
        if alias == '__global__':
            # 提取全局基础类型
            for k, v in data[alias].items():
                if k.startswith('basic_type_'):
                    global_basic_types[k] = v
            continue
        # 识别区划分方案、预处理、后处理、OCR引擎
        if 'pkl5' in data[alias]:
            area_info = data[alias]['pkl5']  # 假设结构为 {区名: {...}}
            schemes[alias] = area_info
    return schemes, global_basic_types

def exec_code(code_str, local_vars):
    """
    动态执行代码字符串，local_vars为本地变量字典
    """
    try:
        exec(code_str, {}, local_vars)
    except Exception as e:
        print(f'执行动态代码出错: {e}')


def recognize_images(classify_result: dict) -> dict:
    """
    主识别流程
    classify_result: {图片名: 类别}
    返回: {图片名: [ {area_name, type, coords, text}, ... ] }
    """
    # 路径准备
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scripts_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(scripts_dir)
    pkl_path = os.path.join(project_dir, 'mu_ban', 'shared_data.pkl')
    images_dir = os.path.join(project_dir, 'lin_shi', 'dai_shi_bie')

    # 读取识别区划分方案等
    schemes, global_basic_types = load_recognition_schemes(pkl_path)

    # 获取access_token
    access_token = get_access_token()
    if not access_token:
        print('获取access_token失败，无法进行百度OCR识别！')
        return {}

    # 读取pkl3标注
    with open(pkl_path, 'rb') as f:
        all_data = pickle.load(f)

    results = {}
    for img_name, img_type in classify_result.items():
        img_path = os.path.join(images_dir, img_name)
        image = cv2.imread(img_path)
        if image is None:
            results[img_name] = [{'error': '图片无法读取'}]
            continue
        img_result = []
        # 读取该图片的pkl3标注
        pkl3_data = all_data.get(img_type, {}).get('pkl3', {})
        boxes = pkl3_data.get('boxes', [])
        # 遍历所有框，按type对应basic_type_x
        for box in boxes:
            box_type = box.get('type')
            area_name = box.get('area_name') or f'basic_type_{box_type}'
            pt1 = box.get('pt1')
            pt2 = box.get('pt2')
            print(f"[调试] box: type={box_type}, area_name={area_name}, pt1={pt1}, pt2={pt2}")
            if not (1 <= box_type <= 4):
                continue
            basic_type_key = f'basic_type_{box_type}'
            area_info = global_basic_types.get(basic_type_key, {})
            if not pt1 or not pt2:
                img_result.append({'area_name': area_name, 'type': box_type, 'coords': None, 'text': '无区域坐标'})
                print(f"[调试] 跳过box: type={box_type}, area_name={area_name}，无坐标")
                continue
            x1, y1 = pt1
            x2, y2 = pt2
            roi = image[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
            pre_code = area_info.get('预处理方案', '')
            if pre_code:
                local_vars = {'img': roi, 'np': np, 'cv2': cv2}
                exec_code(pre_code, local_vars)
                roi = local_vars.get('img', roi)
            ocr_engine_name = area_info.get('OCR引擎', 'tesseractOCR')
            ocr_func = OCR_ENGINES.get(ocr_engine_name, tesseract_ocr)
            if ocr_engine_name == '百度OCR':
                ocr_result = ocr_func(roi, access_token)
            else:
                ocr_result = ocr_func(roi)
            post_code = area_info.get('后处理方案', '')
            if post_code:
                local_vars = {'text': ocr_result}
                exec_code(post_code, local_vars)
                ocr_result = local_vars.get('text', ocr_result)
            print(f"[调试] box识别内容: type={box_type}, area_name={area_name}, text={ocr_result}")
            img_result.append({
                'area_name': area_name,
                'type': box_type,
                'coords': (x1, y1, x2, y2),
                'text': ocr_result
            })
        # 2. 处理pkl5下的所有非basic_type_x区（如有）
        type_scheme = schemes.get(img_type)
        if type_scheme:
            for area_name, area_info in type_scheme.items():
                if area_name.startswith('basic_type_'):
                    continue  # 跳过与全局重复的basic_type_x
                coords = area_info.get('coords')
                if not coords:
                    img_result.append({'area_name': area_name, 'type': None, 'coords': None, 'text': '无区域坐标'})
                    print(f"[调试] 跳过pkl5区: area_name={area_name}，无坐标")
                    continue
                x1, y1, x2, y2 = coords
                roi = image[y1:y2, x1:x2]
                pre_code = area_info.get('预处理方案', '')
                if pre_code:
                    local_vars = {'img': roi, 'np': np, 'cv2': cv2}
                    exec_code(pre_code, local_vars)
                    roi = local_vars.get('img', roi)
                ocr_engine_name = area_info.get('OCR引擎', 'tesseractOCR')
                ocr_func = OCR_ENGINES.get(ocr_engine_name, tesseract_ocr)
                if ocr_engine_name == '百度OCR':
                    ocr_result = ocr_func(roi, access_token)
                else:
                    ocr_result = ocr_func(roi)
                post_code = area_info.get('后处理方案', '')
                if post_code:
                    local_vars = {'text': ocr_result}
                    exec_code(post_code, local_vars)
                    ocr_result = local_vars.get('text', ocr_result)
                print(f"[调试] pkl5区识别内容: area_name={area_name}, text={ocr_result}")
                img_result.append({
                    'area_name': area_name,
                    'type': None,
                    'coords': (x1, y1, x2, y2),
                    'text': ocr_result
                })
        results[img_name] = img_result
    return results

def recognize_with_progress(classify_result):
    total = len(classify_result)
    ocr_result = {}
    def process_func(update_copy, update_judge, update_recognize):
        update_copy(total)
        update_judge(total)
        processed = 0
        for img_name, img_type in classify_result.items():
            single_result = recognize_images({img_name: img_type})
            ocr_result.update(single_result)
            processed += 1
            update_recognize(processed)
    show_progress_window(total, total, total, process_func)
    return ocr_result

if __name__ == '__main__':
    # 演示用：假设有分类结果
    classify_result = {'test1.jpg': 'san_tu', 'test2.jpg': 'si_tu'}
    res = recognize_images(classify_result)
    print(res) 