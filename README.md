# corneal-topography-OCR

本项目用于对特定格式的带文字图片（如角膜地形图）进行字符识别和提取，支持自定义结构类型判别、识别区划分、预处理和后处理方案。识别结果以结构类型-图片名字-各类型识别区识别结果的格式保存为 Excel 文件。

---

## 项目结构

```
corneal-topography-OCR/
├── scripts/                # 主要脚本目录
│   ├── bian_ji/            # 编辑/标注相关脚本
│   │   ├── pklmain.py
│   │   ├── pkl1.py ~ pkl5.py
│   │   └── data_manager.py
│   ├── shi_bie/            # 识别/导出相关脚本
│   │   ├── ocrmain.py
│   │   ├── ocr1.py ~ ocr6.py
│   │   └── test_baidu_ocr.py
│   └── __pycache__/
├── mu_ban/                 # 配置与模板
│   ├── shared_data.pkl
│   ├── baidu_ocr_key.txt
│   ├── edit_shared_data.py
│   └── view_pkl.py
├── lin_shi/                # 临时图片文件夹（可为空）
├── results/                # 识别结果输出（Excel文件）
│   └── ocr_results_*.xlsx
├── 原始图片们/             # 原始图片存放目录
│   └── image_001.jpg ...
├── dist/                   # 可执行文件输出目录（不建议加入版本库）
├── README.md               # 项目说明
├── requirements.txt        # 依赖列表
└── .gitignore              # Git 忽略规则
```

---

## 主要功能

- **图片字符识别与提取**：对特定格式的角膜地形图等图片进行文字识别，支持自定义结构类型和识别区划分。
- **编辑/标注流程**：可视化标注图片结构，便于后续批量识别。
- **识别结果导出**：识别结果自动保存为 Excel 文件，便于后续分析和整理。
- **配置管理**：支持通过脚本编辑和查看主配置文件（shared_data.pkl）。
- **支持多种预处理、后处理方案**，可灵活扩展。

---

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置百度OCR密钥
在 `mu_ban/baidu_ocr_key.txt` 填写 API_KEY 和 SECRET_KEY。

### 3. 编辑/标注流程
```bash
python scripts/bian_ji/pklmain.py
```
按界面提示操作，完成图片标注。

### 4. 识别/导出流程
```bash
python scripts/shi_bie/ocrmain.py
```
按界面提示完成图片识别和结果导出。

### 5. 编辑/查看配置
- 编辑：`python mu_ban/edit_shared_data.py`
- 查看：`python mu_ban/view_pkl.py`

### 6. 结果查看
识别结果保存在 `results/` 文件夹下，格式为 Excel 文件。

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

---

## 常见问题与注意事项

### 1. 版本控制与 .gitignore 说明

本项目的 `.gitignore` 已设置忽略以下内容：

- `deepseek_chat/` 文件夹
- Python 编译文件（`__pycache__`、`*.pyc` 等）
- 虚拟环境文件夹（`.venv/`、`venv/` 等）
- IDE 配置文件（`.idea/`、`.vscode/` 等）
- 日志文件（`*.log`）
- 数据库文件（`db.sqlite3`、`*.db`、`*.sqlite3`）

这样设置可以避免将本地环境、临时文件、敏感数据等无关内容提交到仓库，保证仓库整洁。

### 2. 大文件管理

> **注意：GitHub 不允许单个文件超过 100MB。**

如有大于 100MB 的文件（如 `dist/` 目录下的 `.exe` 文件），请勿提交到仓库。建议将此类文件加入 `.gitignore`，如：

```gitignore
dist/
```

如需同步大文件，可考虑使用 [Git LFS](https://git-lfs.github.com/)。

### 3. 数据库文件

数据库文件（如 `db.sqlite3`）通常只用于本地开发和测试，不建议加入版本库。建议通过迁移脚本或初始化脚本来管理数据库结构和初始数据。

---

