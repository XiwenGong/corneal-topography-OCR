import pickle
import os
import re

PKL_PATH = os.path.join(os.path.dirname(__file__), 'shared_data.pkl')

# 正则匹配 def judge/def judege/def judg/def jugde 等各种拼写
FUNC_DEF_PATTERN = re.compile(r'def\s+j\w{2,5}ge\s*\(')

with open(PKL_PATH, 'rb') as f:
    data = pickle.load(f)

changed = False
for alias, scripts in data.items():
    if 'pkl2' in scripts and '图片类型判别方案' in scripts['pkl2']:
        code = scripts['pkl2']['图片类型判别方案']
        # 只要不是 def judge( 就替换
        new_code = re.sub(r'def\s+\w+\s*\(', 'def judge(', code)
        if new_code != code:
            print(f"修正 {alias} 的判别方案函数名为 judge")
            scripts['pkl2']['图片类型判别方案'] = new_code
            changed = True

if changed:
    with open(PKL_PATH, 'wb') as f:
        pickle.dump(data, f)
    print("已自动修正并保存 shared_data.pkl！")
else:
    print("无需修正，所有函数名均为 judge。") 