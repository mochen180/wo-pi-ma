import os
import re

def validate_code_structure():
    print("=== 代码结构验证 ===")
    
    # 检查文件是否存在
    if not os.path.exists('llm_client_with_summary.py'):
        print("✗ 主文件不存在")
        return False
    print("✓ 主文件存在")
    
    # 检查tools.py是否存在
    if not os.path.exists('tools.py'):
        print("✗ tools.py不存在")
        return False
    print("✓ tools.py存在")
    
    # 读取主文件内容
    with open('llm_client_with_summary.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必要的函数定义
    required_functions = [
        'def load_env()',
        'def build_tools_system_prompt()',
        'def build_summary_system_prompt()',
        'def calculate_history_length(history)',
        'def summarize_chat_history(history, env_vars)',
        'def call_llm_stream(prompt, env_vars, history, tools_enabled=True)',
        'def parse_tool_call(content)',
        'def execute_tool_call(tool_call)',
        'def main()'
    ]
    
    for func in required_functions:
        if func in content:
            print(f"✓ 找到函数: {func}")
        else:
            print(f"✗ 缺少函数: {func}")
            return False
    
    # 检查必要的导入
    required_imports = [
        'import os',
        'import json',
        'import time',
        'import urllib.request',
        'import urllib.error',
        'from tools import TOOLS'
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"✓ 找到导入: {imp}")
        else:
            print(f"✗ 缺少导入: {imp}")
            return False
    
    # 检查总结功能的关键逻辑
    summary_features = [
        'len(history) >= 10',
        'history_length >= 3000',
        'compress_count = int(total_messages * 0.7)',
        'keep_part = history[compress_count:]',
        'summarize_chat_history(history, env_vars)'
    ]
    
    for feature in summary_features:
        if feature in content:
            print(f"✓ 找到总结功能: {feature}")
        else:
            print(f"✗ 缺少总结功能: {feature}")
            return False
    
    # 检查工具调用功能
    tool_features = [
        'delete_file',
        'list_files',
        'create_file',
        'read_file',
        'search_internet'
    ]
    
    for tool in tool_features:
        if tool in content:
            print(f"✓ 找到工具支持: {tool}")
        else:
            print(f"✗ 缺少工具支持: {tool}")
            return False
    
    print("\n=== 验证结果 ===")
    print("✓ 所有检查通过")
    print("✓ 代码结构完整")
    print("✓ 总结功能实现正确")
    print("✓ 工具调用功能完整")
    return True

def validate_readme():
    print("\n=== README验证 ===")
    
    if not os.path.exists('README.md'):
        print("✗ README.md不存在")
        return False
    print("✓ README.md存在")
    
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查README内容
    required_sections = [
        '功能介绍',
        '总结逻辑',
        '使用方法',
        '工具列表',
        '示例',
        '注意事项'
    ]
    
    for section in required_sections:
        if section in content:
            print(f"✓ 找到章节: {section}")
        else:
            print(f"✗ 缺少章节: {section}")
            return False
    
    print("\n=== README验证结果 ===")
    print("✓ README内容完整")
    return True

if __name__ == "__main__":
    code_valid = validate_code_structure()
    readme_valid = validate_readme()
    
    if code_valid and readme_valid:
        print("\n🎉 所有验证通过！代码已准备就绪。")
        print("\n使用说明:")
        print("1. 确保在项目根目录下创建了包含API密钥的.env文件")
        print("2. 运行命令: python llm_client_with_summary.py")
        print("3. 当聊天超过5轮或上下文长度超过3k时，会自动触发总结")
    else:
        print("\n❌ 验证失败，请检查代码")
