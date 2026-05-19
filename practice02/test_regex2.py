import re

# 测试删除文件命令的正则表达式
def test_delete_regex():
    test_cases = [
        "删除env.example文件",
        "删除venv目录下的env.example文件",
        "删除practice02目录下的example2.txt文件",
        "删除practice02下的example1.txt文件",
        "删除practice02中的test.txt文件"
    ]
    
    print("=== 测试删除文件命令的正则表达式 ===")
    for test in test_cases:
        match = re.search(r'删除(?:(.*?)(?:目录下的|下的|中的|目录的))?(.*?)文件', test)
        if match:
            directory = match.group(1).strip() if match.group(1) else ""
            filename = match.group(2).strip()
            print(f"输入: {test}")
            print(f"匹配结果: 目录='{directory}', 文件名={filename}")
        else:
            print(f"输入: {test}")
            print("匹配失败")
        print()

if __name__ == "__main__":
    test_delete_regex()
