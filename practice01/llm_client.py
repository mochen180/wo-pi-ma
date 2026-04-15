import os
import json
import time
from urllib.parse import urlparse
from http.client import HTTPConnection, HTTPSConnection


def load_env():
    """加载环境变量"""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    env_vars = {}
    
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return env_vars
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
                    except ValueError:
                        print(f"Warning: Invalid line in .env file: {line}")
    except Exception as e:
        print(f"Error reading .env file: {e}")
    
    return env_vars


def call_llm(prompt, env_vars):
    """调用LLM API并返回结果和统计信息"""
    # 获取配置
    base_url = env_vars.get('BASE_URL', 'http://127.0.0.1:1234')
    model = env_vars.get('MODEL', 'qwen3.5-4b')
    api_key = env_vars.get('API_KEY', 'qwen3.5-4b')
    max_tokens = int(env_vars.get('MAX_TOKENS', 1000))
    temperature = float(env_vars.get('TEMPERATURE', 0.7))
    
    # 验证必要参数
    if not api_key:
        return {'error': 'API_KEY is required'}
    
    # 解析URL
    try:
        parsed_url = urlparse(base_url)
        host = parsed_url.netloc
        path = parsed_url.path or '/v1'
        if not path.endswith('/'):
            path += '/'
        path += 'chat/completions'
    except Exception as e:
        return {'error': f'Invalid BASE_URL: {e}'}
    
    # 准备请求数据
    data = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'temperature': temperature
    }
    
    # 记录开始时间
    start_time = time.time()
    
    # 发送请求
    conn = None
    try:
        # 修复：统一使用4个空格缩进
        if parsed_url.scheme == 'https':
            conn = HTTPSConnection(host, timeout=30)
        else:
            conn = HTTPConnection(host, timeout=30)

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        conn.request('POST', path, body=json.dumps(data), headers=headers)
        response = conn.getresponse()
        
        # 检查响应状态
        if response.status != 200:
            response_data = response.read().decode('utf-8')
            return {'error': f'API error: {response.status} - {response_data}'}
        
        response_data = response.read().decode('utf-8')
        response_json = json.loads(response_data)
        
        # 计算耗时
        elapsed_time = time.time() - start_time
        
        # 提取token使用情况
        usage = response_json.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 计算token/s速度
        tokens_per_second = total_tokens / elapsed_time if elapsed_time > 0 else 0
        
        # 提取响应内容
        content = response_json.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return {
            'content': content,
            'usage': {
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens
            },
            'time': elapsed_time,
            'tokens_per_second': tokens_per_second
        }
    except Exception as e:
        return {'error': f'Connection error: {e}'}
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    # 加载环境变量
    env_vars = load_env()
    
    # 检查必要的环境变量
    if not env_vars.get('API_KEY'):
        print('Error: API_KEY not found in .env file')
        print('Please create a .env file based on env.example and fill in your API key')
        exit(1)
    
    # 测试prompt
    prompt = '请简单介绍一下Python编程语言'
    
    print('Calling LLM API...')
    result = call_llm(prompt, env_vars)
    
    if 'error' in result:
        print(f'Error: {result["error"]}')
    else:
        print('\nResponse:')
        print(result['content'])
        print('\nStatistics:')
        print(f'Prompt tokens: {result["usage"]["prompt_tokens"]}')
        print(f'Completion tokens: {result["usage"]["completion_tokens"]}')
        print(f'Total tokens: {result["usage"]["total_tokens"]}')
        print(f'Time taken: {result["time"]:.2f} seconds')
        print(f'Tokens per second: {result["tokens_per_second"]:.2f}')