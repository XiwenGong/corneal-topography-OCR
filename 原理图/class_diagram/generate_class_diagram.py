#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用Graphviz生成项目主要类图的脚本
"""

from graphviz import Digraph


def create_project_class_diagram():
    """
    创建项目的主要类图
    """
    dot = Digraph(comment='角膜地形图OCR项目类图', format='png')
    dot.attr(rankdir='BT')  # 设置方向为自下而上
    
    # 设置节点和边的字体为支持中文的字体
    dot.attr('node', shape='record', fontname='Microsoft YaHei')
    dot.attr('edge', fontname='Microsoft YaHei')
    
    # 数据管理相关类
    dot.node('DataManager', '{DataManager|+ pkl_file: str\\l+ data: Dict\\l|+ __init__(pkl_file: str)\\l+ _load_data() -> Dict\\l+ save_data(alias: str, script_name: str, data: dict) -> bool\\l+ get_data(alias: str, script_name: str) -> Any\\l+ set_global_data(key: str, value: any) -> bool\\l+ get_global_data(key: str) -> any\\l}')
    
    # 编辑模块类
    dot.node('ImageWindow', '{ImageWindow|+ original_pixmap: QPixmap\\l+ saved_size: tuple\\l+ saved_alias: str\\l+ data_manager: DataManager\\l|+ __init__(data_manager: DataManager)\\l+ dragEnterEvent(event: QDragEnterEvent)\\l+ dropEvent(event: QDropEvent)\\l+ save_current_size()\\l}')
    
    dot.node('TypeSchemeWindow', '{TypeSchemeWindow|+ alias: str\\l+ data_manager: DataManager\\l|+ __init__(alias: str, data_manager: DataManager)\\l+ load_existing_scheme()\\l+ save_scheme()\\l}')
    
    dot.node('ShowImageWindow', '{ShowImageWindow|+ data_manager: DataManager\\l+ alias: str\\l+ image_path: str\\l+ size: tuple\\l|+ __init__(image_path: str, size: tuple, alias: str, data_manager: DataManager)\\l+ end_annotate()\\l}')
    
    dot.node('OCREditWindow', '{OCREditWindow|+ alias: str\\l+ data_manager: DataManager\\l|+ __init__(alias: str, data_manager: DataManager)\\l+ load_existing()\\l+ save_data()\\l}')
    
    dot.node('BasicTypeEditWindow', '{BasicTypeEditWindow|+ data_manager: DataManager\\l|+ __init__(data_manager: DataManager)\\l+ load_existing()\\l+ save_data()\\l}')
    
    # 识别模块类
    dot.node('DropWindow', '{DropWindow|+ target_dir: str\\l|+ __init__()\\l+ dragEnterEvent(event: QDragEnterEvent)\\l+ dropEvent(event: QDropEvent)\\l+ is_image_file(file_path: str) -> bool\\l}')
    
    dot.node('ResultOverlayWindow', '{ResultOverlayWindow|+ image_paths: list\\l+ ocr_results: dict\\l+ index: int\\l|+ __init__(image_paths: list, ocr_results: dict, get_display_info_func)\\l+ show_result(index: int, display_info: dict)\\l+ paintEvent(event)\\l}')
    
    dot.node('ProgressWindow', '{ProgressWindow|+ total_copy: int\\l+ total_judge: int\\l+ total_recognize: int\\l|+ __init__(total_copy: int, total_judge: int, total_recognize: int)\\l+ update_copy(val: int)\\l+ update_judge(val: int)\\l+ update_recognize(val: int)\\l}')
    
    # 添加关系
    # 编辑模块关系
    dot.edge('ImageWindow', 'DataManager', '使用')
    dot.edge('TypeSchemeWindow', 'DataManager', '使用')
    dot.edge('ShowImageWindow', 'DataManager', '使用')
    dot.edge('OCREditWindow', 'DataManager', '使用')
    dot.edge('BasicTypeEditWindow', 'DataManager', '使用')
    
    # 识别模块关系
    dot.edge('ResultOverlayWindow', 'ProgressWindow', '使用')
    
    # 保存图片
    dot.render('原理图/class_diagram/project_class_diagram', view=False)

if __name__ == '__main__':
    create_project_class_diagram() 