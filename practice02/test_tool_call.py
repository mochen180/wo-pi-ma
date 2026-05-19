import os
import json
import sys
from tools import TOOLS

# 模拟用户输入
def test_tool_call():
    print("=== 测试工具调用功能 ===")
    
    # 测试1: 删除文件
    print("\n测试1: 删除文件")
    print("用户输入: 删除practice02目录下的examples1.txt文件")
    
    # 手动创建工具调用
    tool_call = {
        "tool_name": "delete_file",
        "parameters": {
            "directory": "practice02",
            "filename": "examples1.txt"
        }
    }
    
    print(f"生成的工具调用: {json.dumps(tool_call, ensure_ascii=False)}")
    
    # 执行工具调用
    if tool_call['tool_name'] in TOOLS:
        tool_function = TOOLS[tool_call['tool_name']]['function']
        result = tool_function(**tool_call['parameters'])
        print(f"工具执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"未知工具: {tool_call['tool_name']}")
    
    # 测试2: 列出文件
    print("\n测试2: 列出文件")
    print("用户输入: 列出practice02目录的文件")
    
    # 手动创建工具调用
    tool_call = {
        "tool_name": "list_files",
        "parameters": {
            "directory": "practice02"
        }
    }
    
    print(f"生成的工具调用: {json.dumps(tool_call, ensure_ascii=False)}")
    
    # 执行工具调用
    if tool_call['tool_name'] in TOOLS:
        tool_function = TOOLS[tool_call['tool_name']]['function']
        result = tool_function(**tool_call['parameters'])
        print(f"工具执行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    else:
        print(f"未知工具: {tool_call['tool_name']}")

if __name__ == "__main__":
    test_tool_call()
