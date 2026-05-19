import os
import json
import time
import urllib.request
import urllib.error
import sys
from tools import TOOLS

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {
        'BASE_URL': 'http://localhost:11434/api/chat',  # 默认使用本地Ollama服务
        'MODEL': 'llama3',  # 默认使用llama3模型
        'API_KEY': ''  # 本地部署通常不需要API密钥
    }
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        env_vars[key] = value
        except Exception as e:
            print(f"读取.env文件时出错: {str(e)}")
    else:
        print("未找到.env文件，使用默认本地部署配置")
    return env_vars

# 构建工具调用的系统提示词
def build_tools_system_prompt():
    tools_description = []
    for tool_name, tool_info in TOOLS.items():
        tool_desc = f"- {tool_name}: {tool_info['description']}\n"
        tool_desc += f"  参数: {json.dumps(tool_info['parameters'], ensure_ascii=False, indent=2)}"
        tools_description.append(tool_desc)
    
    system_prompt = """你是一个文件操作执行器，你的唯一任务是执行用户的文件操作请求。你必须严格按照以下格式生成工具调用：

**工具列表：**
""" + "\n".join(tools_description) + """

**指令：**
1. 当用户要求删除文件时，你必须生成：{"tool_name": "delete_file", "parameters": {"directory": "目录路径", "filename": "文件名"}}
2. 当用户要求列出文件时，你必须生成：{"tool_name": "list_files", "parameters": {"directory": "目录路径"}}
3. 当用户要求创建文件时，你必须生成：{"tool_name": "create_file", "parameters": {"directory": "目录路径", "filename": "文件名", "content": "文件内容"}}
4. 当用户要求读取文件时，你必须生成：{"tool_name": "read_file", "parameters": {"directory": "目录路径", "filename": "文件名"}}
5. 当用户要求搜索互联网时，你必须生成：{"tool_name": "search_internet", "parameters": {"query": "搜索词"}}

**格式要求：**
- 只能生成一行JSON
- 不能有任何其他文本
- 不能有注释
- 不能有多余的空格
- 必须使用双引号
- 必须包含所有必需的参数

**示例：**
用户输入：删除practice02目录下的examples1.txt文件
你必须输出：{"tool_name": "delete_file", "parameters": {"directory": "practice02", "filename": "examples1.txt"}}

用户输入：列出practice02目录的文件
你必须输出：{"tool_name": "list_files", "parameters": {"directory": "practice02"}}

用户输入：在practice02目录创建test.txt文件，内容为Hello
你必须输出：{"tool_name": "create_file", "parameters": {"directory": "practice02", "filename": "test.txt", "content": "Hello"}}

**注意：**
- 你是一个执行器，不是一个解释器
- 你必须直接生成工具调用，不能有任何解释
- 你必须按照用户的要求准确执行操作
- 你只能生成JSON格式的工具调用，不能生成其他任何内容

现在开始执行用户的请求。"""
    
    return system_prompt

# 构建总结聊天记录的系统提示词
def build_summary_system_prompt():
    return """你是一个聊天记录总结助手，你的任务是对用户和AI之间的对话进行总结。

**指令：**
1. 分析对话历史，提取关键信息和主题
2. 生成简洁明了的总结，保留重要内容
3. 总结应该涵盖对话的主要内容和结论
4. 保持总结的客观性和准确性

**格式要求：**
- 以"聊天总结："开头
- 使用简洁的语言，避免冗余
- 重点总结用户的问题和AI的回答
- 不要包含与对话无关的内容

现在开始对以下对话进行总结："""

# 计算聊天历史的总长度
def calculate_history_length(history):
    total_length = 0
    for msg in history:
        if 'content' in msg:
            total_length += len(msg['content'])
    return total_length

# 触发聊天记录总结
def summarize_chat_history(history, env_vars):
    print("\n[触发聊天记录总结...]")
    
    # 计算需要压缩的部分和保留的部分
    total_messages = len(history)
    compress_count = int(total_messages * 0.7)
    keep_count = total_messages - compress_count
    
    # 分离需要压缩的部分和保留的部分
    compress_part = history[:compress_count]
    keep_part = history[compress_count:]
    
    # 构建总结提示词
    summary_prompt = build_summary_system_prompt()
    
    # 添加需要压缩的聊天记录
    for msg in compress_part:
        role = "用户" if msg['role'] == "user" else "AI"
        summary_prompt += f"\n{role}: {msg['content']}"
    
    # 调用LLM进行总结
    base_url = env_vars.get('BASE_URL', 'http://localhost:11434/api/chat')
    model = env_vars.get('MODEL', 'llama3')
    api_key = env_vars.get('API_KEY', '')
    
    # 构建请求数据
    messages = [
        {"role": "system", "content": build_summary_system_prompt()}
    ]
    
    for msg in compress_part:
        messages.append(msg)
    
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": False
    }
    
    # 构建请求
    headers = {
        "Content-Type": "application/json"
    }
    
    # 如果提供了API密钥，则添加Authorization头
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        # 发送请求
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
            
            if 'error' in response_data:
                print(f"总结失败: {response_data['error']}")
                return history
            
            summary = response_data['choices'][0]['message']['content']
            
            print(f"[聊天记录总结完成]")
            print(f"总结内容: {summary}")
            
            # 构建新的历史记录：总结 + 保留的部分
            new_history = [
                {"role": "assistant", "content": f"[聊天总结]\n{summary}"}
            ] + keep_part
            
            return new_history
    
    except Exception as e:
        print(f"总结过程中出错: {str(e)}")
        return history

# 流式调用LLM API
def call_llm_stream(prompt, env_vars, history, tools_enabled=True):
    base_url = env_vars.get('BASE_URL', 'http://localhost:11434/api/chat')
    model = env_vars.get('MODEL', 'llama3')
    api_key = env_vars.get('API_KEY', '')
    
    # 构建消息历史
    messages = []
    
    # 添加系统提示词（仅在第一次或工具启用时）
    if tools_enabled and len(history) == 0:
        system_prompt = build_tools_system_prompt()
        messages.append({"role": "system", "content": system_prompt})
    
    # 添加历史记录
    for msg in history:
        messages.append(msg)
    
    # 添加当前用户输入
    messages.append({"role": "user", "content": prompt})
    
    # 构建请求数据（兼容Ollama格式）
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": True
    }
    
    # 构建请求
    headers = {
        "Content-Type": "application/json"
    }
    
    # 如果提供了API密钥，则添加Authorization头
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    start_time = time.time()
    content = ""
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    
    try:
        # 发送请求
        req = urllib.request.Request(base_url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            # 流式读取响应
            for line in response:
                line = line.strip()
                if not line:
                    continue
                
                # 处理SSE格式
                if line.startswith(b'data: '):
                    line = line[6:]
                    
                    if line == b'[DONE]':
                        break
                    
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        
                        # 检查是否有错误
                        if 'error' in chunk:
                            return {
                                'error': chunk['error'],
                                'time_taken': time.time() - start_time
                            }
                        
                        # 提取token使用情况（仅在最后一个chunk中）
                        if 'usage' in chunk:
                            usage = chunk['usage']
                            prompt_tokens = usage.get('prompt_tokens', 0)
                            completion_tokens = usage.get('completion_tokens', 0)
                            total_tokens = usage.get('total_tokens', 0)
                        
                        # 提取响应内容
                        choices = chunk.get('choices', [])
                        if choices:
                            delta = choices[0].get('delta', {})
                            if 'content' in delta:
                                content += delta['content']
                                print(delta['content'], end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        
        end_time = time.time()
        total_time = end_time - start_time
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        
        # 添加助手响应到历史记录
        history.append({"role": "assistant", "content": content})
        
        return {
            'content': content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'time_taken': total_time,
            'tokens_per_second': tokens_per_second,
            'history': history
        }
        
    except urllib.error.HTTPError as e:
        end_time = time.time()
        total_time = end_time - start_time
        return {
            'error': f"HTTP Error: {e.code} - {e.reason}",
            'time_taken': total_time
        }
    except Exception as e:
        end_time = time.time()
        total_time = end_time - start_time
        return {
            'error': f"Error: {str(e)}",
            'time_taken': total_time
        }

# 解析工具调用
def parse_tool_call(content):
    try:
        # 查找JSON格式的工具调用
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{') and line.endswith('}'):
                try:
                    tool_call = json.loads(line)
                    if 'tool_name' in tool_call and 'parameters' in tool_call:
                        return tool_call
                except json.JSONDecodeError:
                    continue
        return None
    except Exception:
        return None

# 执行工具调用
def execute_tool_call(tool_call):
    tool_name = tool_call['tool_name']
    parameters = tool_call['parameters']
    
    if tool_name not in TOOLS:
        return {
            'success': False,
            'error': f'未知工具: {tool_name}'
        }
    
    tool_info = TOOLS[tool_name]
    tool_function = tool_info['function']
    
    try:
        result = tool_function(**parameters)
        return result
    except Exception as e:
        return {
            'success': False,
            'error': f'执行工具失败: {str(e)}'
        }

# 主函数
def main():
    env_vars = load_env()
    history = []
    
    print("=== LLM 聊天记录总结工具 ===")
    print("你可以使用以下工具:")
    for tool_name in TOOLS.keys():
        print(f"  - {tool_name}: {TOOLS[tool_name]['description']}")
    print("\n输入你的问题或文件操作请求，按Enter发送。按Ctrl+C退出。")
    print("当聊天超过5轮或上下文长度超过3k时，会自动触发聊天记录总结。")
    print("=" * 60)
    
    try:
        while True:
            # 检查是否需要触发总结
            history_length = calculate_history_length(history)
            if len(history) >= 10 or history_length >= 3000:  # 5轮对话是10条消息（用户+助手）
                history = summarize_chat_history(history, env_vars)
                print("\n[聊天记录已压缩]")
                print("=" * 60)
            
            # 读取用户输入
            try:
                prompt = input("\n您: ")
            except EOFError:
                break
            
            if not prompt.strip():
                continue
            
            # 检查是否是直接命令格式
            direct_command = None
            
            # 解析删除文件命令
            if "删除" in prompt and "文件" in prompt:
                import re
                # 匹配多种格式：删除X目录下的Y文件、删除X下的Y文件、删除X中的Y文件、删除Y文件（根目录）
                match = re.search(r'删除(?:(.*?)(?:目录下的|下的|中的|目录的))?(.*?)文件', prompt)
                if match:
                    directory = match.group(1).strip() if match.group(1) else ""
                    filename = match.group(2).strip()
                    direct_command = {
                        "tool_name": "delete_file",
                        "parameters": {
                            "directory": directory,
                            "filename": filename
                        }
                    }
            
            # 解析列出文件命令
            elif "列出" in prompt and "文件" in prompt:
                import re
                # 匹配多种格式：列出X目录的文件、列出X的文件
                match = re.search(r'列出(.*?)(?:目录的|的)文件', prompt)
                if match:
                    directory = match.group(1).strip()
                    direct_command = {
                        "tool_name": "list_files",
                        "parameters": {
                            "directory": directory
                        }
                    }
            
            # 解析读取文件命令
            elif "读取" in prompt and "文件" in prompt:
                import re
                # 匹配多种格式：读取X目录下的Y文件、读取X下的Y文件、读取X中的Y文件
                match = re.search(r'读取(.*?)(?:目录下的|下的|中的|目录的)(.*?)文件', prompt)
                if match:
                    directory = match.group(1).strip()
                    filename = match.group(2).strip()
                    direct_command = {
                        "tool_name": "read_file",
                        "parameters": {
                            "directory": directory,
                            "filename": filename
                        }
                    }
            
            # 解析创建文件命令
            elif "创建" in prompt and "文件" in prompt:
                import re
                # 匹配多种格式：在X目录创建Y文件，内容为Z、在X创建Y文件，内容为Z
                match = re.search(r'在(.*?)(?:目录)?创建(.*?)文件，内容为(.*)', prompt)
                if match:
                    directory = match.group(1).strip()
                    filename = match.group(2).strip()
                    content = match.group(3).strip()
                    direct_command = {
                        "tool_name": "create_file",
                        "parameters": {
                            "directory": directory,
                            "filename": filename,
                            "content": content
                        }
                    }
            
            # 解析搜索互联网命令
            elif "搜索" in prompt:
                import re
                match = re.search(r'搜索(.*)', prompt)
                if match:
                    query = match.group(1).strip()
                    direct_command = {
                        "tool_name": "search_internet",
                        "parameters": {
                            "query": query
                        }
                    }
            
            # 执行直接命令
            if direct_command:
                print("\nAI: ", end='', flush=True)
                print(f"执行命令: {direct_command['tool_name']}")
                
                # 执行工具调用
                start_time = time.time()
                tool_result = execute_tool_call(direct_command)
                end_time = time.time()
                
                # 显示工具执行结果
                print(f"[工具执行结果]")
                print(json.dumps(tool_result, ensure_ascii=False, indent=2))
                
                # 添加到历史记录
                history.append({"role": "user", "content": prompt})
                history.append({
                    "role": "assistant",
                    "content": f"工具调用结果: {json.dumps(tool_result, ensure_ascii=False)}"
                })
                
                # 显示统计信息
                total_time = end_time - start_time
                print(f"\n统计信息:")
                print(f"提示词token: 0")
                print(f"完成token: 0")
                print(f"总token: 0")
                print(f"耗时: {total_time:.2f}秒")
                print(f"速度: 0.00 token/秒")
            else:
                # 添加用户输入到历史记录
                history.append({"role": "user", "content": prompt})
                
                print("\nAI: ", end='', flush=True)
                
                # 调用LLM API
                result = call_llm_stream(prompt, env_vars, history, tools_enabled=True)
                
                if 'error' in result:
                    print(f"\n错误: {result['error']}")
                    print(f"耗时: {result['time_taken']:.2f}秒")
                    history.pop()
                else:
                    print()
                    content = result['content']
                    
                    # 检查是否有工具调用
                    tool_call = parse_tool_call(content)
                    if tool_call:
                        print(f"\n[检测到工具调用: {tool_call['tool_name']}]")
                        
                        # 执行工具调用
                        tool_result = execute_tool_call(tool_call)
                        
                        # 显示工具执行结果
                        print(f"[工具执行结果]")
                        print(json.dumps(tool_result, ensure_ascii=False, indent=2))
                        
                        # 将工具执行结果添加到历史记录
                        history.append({
                            "role": "assistant",
                            "content": f"工具调用结果: {json.dumps(tool_result, ensure_ascii=False)}"
                        })
                        
                        # 让LLM根据工具执行结果生成最终回复
                        print("\nAI: ", end='', flush=True)
                        follow_up_prompt = "请根据工具执行结果，向用户报告操作结果。"
                        result = call_llm_stream(follow_up_prompt, env_vars, history, tools_enabled=False)
                        
                        if 'error' in result:
                            print(f"\n错误: {result['error']}")
                        else:
                            print()
                
                # 显示统计信息
                if 'result' in locals():
                    print(f"\n统计信息:")
                    print(f"提示词token: {result.get('prompt_tokens', 0)}")
                    print(f"完成token: {result.get('completion_tokens', 0)}")
                    print(f"总token: {result.get('total_tokens', 0)}")
                    print(f"耗时: {result.get('time_taken', 0):.2f}秒")
                    print(f"速度: {result.get('tokens_per_second', 0):.2f} token/秒")
                
            print("=" * 60)
            
    except KeyboardInterrupt:
        print("\n\n聊天已结束。")

if __name__ == "__main__":
    main()