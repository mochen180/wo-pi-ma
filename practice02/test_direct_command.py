import os
import sys

# 测试直接命令执行功能
print("=== 测试直接命令执行功能 ===")

# 首先创建一个测试文件
print("\n1. 创建测试文件")
with open('practice02/test_delete.txt', 'w', encoding='utf-8') as f:
    f.write("这是一个测试文件，用于测试直接命令执行功能。")
print("测试文件已创建: practice02/test_delete.txt")

# 测试删除文件命令
print("\n2. 测试删除文件命令")
sys.path.insert(0, 'practice02')
from llm_client_with_tools import execute_tool_call

# 模拟删除文件命令
tool_call = {
    "tool_name": "delete_file",
    "parameters": {
        "directory": "practice02",
        "filename": "test_delete.txt"
    }
}

result = execute_tool_call(tool_call)
print(f"删除文件结果: {result}")

# 验证文件是否被删除
print("\n3. 验证文件是否被删除")
if os.path.exists('practice02/test_delete.txt'):
    print("错误：文件未被删除")
else:
    print("成功：文件已被删除")

# 测试列出文件命令
print("\n4. 测试列出文件命令")
tool_call = {
    "tool_name": "list_files",
    "parameters": {
        "directory": "practice02"
    }
}

result = execute_tool_call(tool_call)
print(f"列出文件结果: {result}")

print("\n=== 测试完成 ===")
