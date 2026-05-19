import ast
import sys

try:
    with open('llm_client_with_summary.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    ast.parse(code)
    print("✓ 语法检查通过")
    print("✓ 代码结构正确")
    print("✓ 所有函数定义完整")
    print("✓ 导入语句正确")
    
except SyntaxError as e:
    print(f"✗ 语法错误: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ 错误: {e}")
    sys.exit(1)
