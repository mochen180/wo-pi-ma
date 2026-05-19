import os
import json
import time
import urllib.request
import urllib.error

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

# 调用LLM API
def call_llm(prompt, env_vars):
    base_url = env_vars.get('BASE_URL', 'https://api.openai.com/v1')
    model = env_vars.get('MODEL', 'gpt-4')
    api_key = env_vars.get('API_KEY', '')
    
    if not api_key:
        raise ValueError("API_KEY not found in .env file")
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    # 构建请求
    # 直接使用base_url作为完整的API端点
    url = base_url
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    start_time = time.time()
    
    try:
        # 发送请求
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            response_data = json.loads(response.read().decode('utf-8'))
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 检查响应是否包含错误
        if 'error' in response_data:
            return {
                'error': response_data['error'],
                'time_taken': total_time
            }
        
        # 提取token使用情况
        usage = response_data.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        # 计算token/s速度
        tokens_per_second = total_tokens / total_time if total_time > 0 else 0
        
        # 提取响应内容
        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return {
            'content': content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'time_taken': total_time,
            'tokens_per_second': tokens_per_second
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
    
    # 测试prompt
    prompt = "请解释什么是人工智能"
    
    print("正在调用LLM API...")
    result = call_llm(prompt, env_vars)
    
    if 'error' in result:
        print(f"错误: {result['error']}")
        print(f"耗时: {result['time_taken']:.2f}秒")
    else:
        print(f"响应内容: {result['content']}")
        print(f"\n统计信息:")
        print(f"提示词token: {result['prompt_tokens']}")
        print(f"完成token: {result['completion_tokens']}")
        print(f"总token: {result['total_tokens']}")
        print(f"耗时: {result['time_taken']:.2f}秒")
        print(f"速度: {result['tokens_per_second']:.2f} token/秒")

if __name__ == "__main__":
    main()