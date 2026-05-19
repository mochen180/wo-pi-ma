import os
import json
import time
import urllib.request
import urllib.error
import sys

# 读取.env文件
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
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
        print("未找到.env文件")
    return env_vars

# 流式调用LLM API
def call_llm_stream(prompt, env_vars, history):
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1/chat/completions')
    model = env_vars.get('MODEL', 'gpt-4')
    api_key = env_vars.get('API_KEY', '')
    
    if not api_key:
        raise ValueError("API_KEY not found in .env file")
    
    # 构建消息历史
    messages = []
    # 添加历史记录
    for msg in history:
        messages.append(msg)
    # 添加当前用户输入
    messages.append({"role": "user", "content": prompt})
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": True  # 启用流式输出
    }
    
    # 构建请求
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
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
                    line = line[6:]  # 去掉'data: '前缀
                    
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
                                # 实时输出内容
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

# 主函数
def main():
    env_vars = load_env()
    history = []  # 聊天历史记录
    
    print("=== LLM 终端聊天工具 ===")
    print("输入您的问题，按Enter发送。按Ctrl+C退出。")
    print("=" * 50)
    
    try:
        while True:
            # 读取用户输入
            try:
                prompt = input("\n您: ")
            except EOFError:
                break
            
            if not prompt.strip():
                continue
            
            # 添加用户输入到历史记录
            history.append({"role": "user", "content": prompt})
            
            print("\nAI: ", end='', flush=True)
            
            # 调用LLM API
            result = call_llm_stream(prompt, env_vars, history)
            
            if 'error' in result:
                print(f"\n错误: {result['error']}")
                print(f"耗时: {result['time_taken']:.2f}秒")
                # 移除最后一条用户输入（因为出错了）
                history.pop()
            else:
                print()  # 换行
                print(f"\n统计信息:")
                print(f"提示词token: {result['prompt_tokens']}")
                print(f"完成token: {result['completion_tokens']}")
                print(f"总token: {result['total_tokens']}")
                print(f"耗时: {result['time_taken']:.2f}秒")
                print(f"速度: {result['tokens_per_second']:.2f} token/秒")
                
            print("=" * 50)
            
    except KeyboardInterrupt:
        print("\n\n聊天已结束。")

if __name__ == "__main__":
    main()
