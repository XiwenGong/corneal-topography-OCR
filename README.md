# corneal-topography-OCR

本项目用于各种具有特定格式的带文字图片（比如某种角膜地形图）的字符识别和提取，

支持自定义结构类型判别方案、划分识别区方案、预处理方案、后处理方案，

识别结果按 结构类型-图片名字-各类型识别区识别结果 的格式保存为excel文件


不过可能主要价值是，他是我调查和体验软件开发全流程的一个个人全栈实践项目



项目原理图见yan_shi文件夹，大概画了用例图、流程图、类图、时序图，

不过是在脚本写好之前画的，所以会和项目目前的实际行为有小出入





，，，，，操作github desktop的时候，一些没被跟踪的文件被永久删除了

其中包括用例图和类图


我草


---

## 目录结构

- scripts/
  - bian_ji/
    - pklmain.py         # 编辑/标注主程序
    - pkl1.py ~ pkl5.py  # 编辑流程各阶段脚本
    - data_manager.py    # 数据管理工具
    - __init__.py
  - shi_bie/
    - ocrmain.py         # 识别/导出主程序
    - ocr1.py ~ ocr6.py  # 识别流程各阶段脚本
    - test_baidu_ocr.py  # 百度OCR测试工具
    - __init__.py
  - __pycache__/

- mu_ban/
  - shared_data.pkl      # 主配置/数据文件
  - baidu_ocr_key.txt    # 百度OCR密钥
  - edit_shared_data.py  # 配置编辑工具
  - view_pkl.py          # 配置查看工具

- lin_shi/               # 临时图片文件夹（可为空）

- results/               # 识别结果输出（Excel文件）
  - ocr_results_*.xlsx

- 原始图片们/            # 原始图片存放目录
  - image_001.jpg ...

- README.md              # 项目说明
- requirements.txt       # 依赖列表

---

## 环境依赖与安装

建议使用 Python 3.10 及以上版本。

安装依赖：
```bash
pip install -r requirements.txt
```

---

## 百度OCR密钥配置

1. 在 [百度智能云OCR](https://cloud.baidu.com/product/ocr/general) 申请 API Key 和 Secret Key。
2. 在 `mu_ban/baidu_ocr_key.txt` 文件中填写如下内容（用你的密钥替换）：

```
API_KEY = "你的APIKEY"
SECRET_KEY = "你的SECRETKEY"
```

---

## 主要功能与使用方法

### 1. 编辑/标注流程
运行：
```bash
python scripts/bian_ji/pklmain.py
```
按界面提示拖拽图片、标注、保存。

### 2. 识别/导出流程
运行：
```bash
python scripts/shi_bie/ocrmain.py
```
按界面提示完成图片识别和结果导出。

### 3. 编辑/查看 shared_data.pkl
- 编辑：`python mu_ban/edit_shared_data.py`
- 查看：`python mu_ban/view_pkl.py`

---

## 结果输出

识别结果会自动保存在 `results/` 文件夹下，格式为 Excel 文件。

---

## 其它说明

- 项目不包含虚拟环境（env/），请用 requirements.txt 自行安装依赖。
- 如遇问题请先检查 Python 版本和依赖安装情况。

---

## License

MIT

