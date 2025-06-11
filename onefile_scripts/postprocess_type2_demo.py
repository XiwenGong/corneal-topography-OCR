"""
类型2后处理方案测试脚本
本脚本用于编写和测试类型2识别区的后处理代码片段。
你可以在这里编辑后处理逻辑，然后将代码复制到编辑窗口进行实际应用。
"""

def postprocess_type2(text):
    """
    类型2后处理方案：只在第三行的时间（xx:xx:xx）前加空格
    """
    text = text.replace(' ', '')
    lines = text.splitlines()
    if len(lines) >= 3:
        import re
        # 匹配最后一个时间串（xx:xx:xx），在其前面加空格
        lines[2] = re.sub(r'(\d{1,2}:\d{2}:\d{2})$', r' \1', lines[2])
    return '\n'.join(lines)

# ===== 测试用例 =====
if __name__ == '__main__':
    # 示例原始OCR结果（三行）
    ocr_text = '''OS
0107猪02
2025/1/711:42:22'''
    result = postprocess_type2(ocr_text)
    print(f'原始: "{ocr_text}"')
    print(f'处理后: "{result}"') 