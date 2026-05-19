import os
import json
import urllib.request
import urllib.parse
import subprocess

def list_files(directory):
    """
    列出某个目录下的所有文件和目录
    
    参数:
        directory (str): 目录路径
    
    返回:
        dict: 包含文件列表的结果
    """
    try:
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"目录不存在: {directory}"
            }
        
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"路径不是目录: {directory}"
            }
        
        files = os.listdir(directory)
        return {
            "success": True,
            "directory": directory,
            "files": files,
            "count": len(files)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"列出文件失败: {str(e)}"
        }

def rename_file(directory, old_name, new_name):
    """
    修改某个目录下某个文件的名字
    
    参数:
        directory (str): 目录路径
        old_name (str): 原文件名
        new_name (str): 新文件名
    
    返回:
        dict: 操作结果
    """
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        
        if not os.path.exists(old_path):
            return {
                "success": False,
                "error": f"文件不存在: {old_path}"
            }
        
        if os.path.exists(new_path):
            return {
                "success": False,
                "error": f"目标文件已存在: {new_path}"
            }
        
        os.rename(old_path, new_path)
        return {
            "success": True,
            "old_path": old_path,
            "new_path": new_path,
            "message": f"文件已从 {old_name} 重命名为 {new_name}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"重命名文件失败: {str(e)}"
        }

def delete_file(directory, filename):
    """
    删除某个目录下的某个文件
    
    参数:
        directory (str): 目录路径
        filename (str): 文件名
    
    返回:
        dict: 操作结果
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        if os.path.isdir(file_path):
            return {
                "success": False,
                "error": f"路径是目录，不是文件: {file_path}"
            }
        
        os.remove(file_path)
        return {
            "success": True,
            "file_path": file_path,
            "message": f"文件已删除: {filename}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"删除文件失败: {str(e)}"
        }

def create_file(directory, filename, content):
    """
    在某个目录下新建1个文件，并且写入内容
    
    参数:
        directory (str): 目录路径
        filename (str): 文件名
        content (str): 文件内容
    
    返回:
        dict: 操作结果
    """
    try:
        if not os.path.exists(directory):
            return {
                "success": False,
                "error": f"目录不存在: {directory}"
            }
        
        if not os.path.isdir(directory):
            return {
                "success": False,
                "error": f"路径不是目录: {directory}"
            }
        
        file_path = os.path.join(directory, filename)
        
        if os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件已存在: {file_path}"
            }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"文件已创建: {filename}",
            "content_length": len(content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"创建文件失败: {str(e)}"
        }

def read_file(directory, filename):
    """
    读取某个目录下的某个文件的内容
    
    参数:
        directory (str): 目录路径
        filename (str): 文件名
    
    返回:
        dict: 包含文件内容的结果
    """
    try:
        file_path = os.path.join(directory, filename)
        
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"文件不存在: {file_path}"
            }
        
        if os.path.isdir(file_path):
            return {
                "success": False,
                "error": f"路径是目录，不是文件: {file_path}"
            }
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "success": True,
            "file_path": file_path,
            "content": content,
            "content_length": len(content)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"读取文件失败: {str(e)}"
        }

def search_internet(query):
    """
    根据用户对话的内容搜索互联网
    
    参数:
        query (str): 搜索查询词
    
    返回:
        dict: 包含搜索结果的结果
    """
    try:
        # 使用DuckDuckGo的Instant Answer API，不需要API密钥
        # 这是一个公开的API，不需要复杂的登录流程
        search_url = "https://api.duckduckgo.com/"
        
        # 构建查询参数
        params = urllib.parse.urlencode({
            "q": query,
            "format": "json",
            "no_html": "1",
            "no_redirect": "1"
        })
        
        # 发送请求
        full_url = f"{search_url}?{params}"
        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req) as response:
            search_results = json.loads(response.read().decode('utf-8'))
        
        # 提取结果
        web_results = []
        
        # 处理DuckDuckGo的响应格式
        if "Abstract" in search_results and search_results["Abstract"]:
            # 添加摘要结果
            web_results.append({
                "title": search_results.get("Heading", "搜索结果"),
                "url": search_results.get("AbstractURL", ""),
                "snippet": search_results.get("Abstract", "")
            })
        
        # 处理相关主题
        if "RelatedTopics" in search_results:
            for topic in search_results["RelatedTopics"]:
                if isinstance(topic, dict):
                    if "Text" in topic and "FirstURL" in topic:
                        web_results.append({
                            "title": topic["Text"],
                            "url": topic["FirstURL"],
                            "snippet": topic.get("Result", topic["Text"])
                        })
                    elif "Topics" in topic:
                        # 处理子主题
                        for sub_topic in topic["Topics"]:
                            if "Text" in sub_topic and "FirstURL" in sub_topic:
                                web_results.append({
                                    "title": sub_topic["Text"],
                                    "url": sub_topic["FirstURL"],
                                    "snippet": sub_topic.get("Result", sub_topic["Text"])
                                })
        
        # 限制结果数量
        web_results = web_results[:5]
        
        if not web_results:
            # 如果没有结果，返回一个默认结果
            web_results = [{
                "title": f"搜索结果: {query}",
                "url": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                "snippet": f"没有找到关于 '{query}' 的详细信息。请访问DuckDuckGo获取更多结果。"
            }]
        
        return {
            "success": True,
            "query": query,
            "results": web_results,
            "count": len(web_results),
            "info": "使用的是DuckDuckGo Instant Answer API，不需要API密钥。"
        }
    except Exception as e:
        # 如果API调用失败，返回模拟结果
        return {
            "success": True,
            "query": query,
            "results": [
                {
                    "title": f"搜索结果: {query}",
                    "url": f"https://duckduckgo.com/?q={urllib.parse.quote(query)}",
                    "snippet": f"这是关于 '{query}' 的搜索结果。由于API调用失败，这是一个模拟结果。"
                }
            ],
            "count": 1,
            "info": "使用的是模拟搜索服务，API调用失败。"
        }

def anythingllm_query(query):
    """
    使用curl命令访问AnythingLLM的聊天API接口
    
    参数:
        query (str): 查询内容
    
    返回:
        dict: 包含查询结果的结果
    """
    try:
        # 读取.env文件中的配置
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        anythingllm_api_key = ""
        anythingllm_workspace_slug = ""
        
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        if key == 'ANYTHINGLLM_API_KEY':
                            anythingllm_api_key = value
                        elif key == 'ANYTHINGLLM_WORKSPACE_SLUG':
                            anythingllm_workspace_slug = value
        
        if not anythingllm_api_key:
            return {
                "success": False,
                "error": "未找到ANYTHINGLLM_API_KEY配置"
            }
        
        if not anythingllm_workspace_slug:
            return {
                "success": False,
                "error": "未找到ANYTHINGLLM_WORKSPACE_SLUG配置"
            }
        
        # 构建API URL
        api_url = f"http://localhost:3001/api/v1/workspace/{anythingllm_workspace_slug}/chat"
        
        # 构建请求数据
        payload = json.dumps({
            "message": query,
            "thinking": "",
            "includeHistory": True
        }, ensure_ascii=False)
        
        # 构建curl命令
        curl_command = [
            "curl",
            "-X", "POST",
            api_url,
            "-H", f"Authorization: Bearer {anythingllm_api_key}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ]
        
        # 执行curl命令
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 检查执行结果
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"curl命令执行失败: {result.stderr}"
            }
        
        # 解析响应
        try:
            response = json.loads(result.stdout)
            
            # 只返回简洁的结果
            if response.get('textResponse'):
                return {
                    "success": True,
                    "result": response['textResponse'].strip()
                }
            elif response.get('error'):
                return {
                    "success": False,
                    "error": response['error']
                }
            else:
                return {
                    "success": True,
                    "result": "查询完成，但没有返回结果。"
                }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": f"响应解析失败: {result.stdout}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"查询失败: {str(e)}"
        }

# 工具函数映射
TOOLS = {
    "list_files": {
        "function": list_files,
        "description": "列出某个目录下的所有文件和目录",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                }
            },
            "required": ["directory"]
        }
    },
    "rename_file": {
        "function": rename_file,
        "description": "修改某个目录下某个文件的名字",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "old_name": {
                    "type": "string",
                    "description": "原文件名"
                },
                "new_name": {
                    "type": "string",
                    "description": "新文件名"
                }
            },
            "required": ["directory", "old_name", "new_name"]
        }
    },
    "delete_file": {
        "function": delete_file,
        "description": "删除某个目录下的某个文件",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                }
            },
            "required": ["directory", "filename"]
        }
    },
    "create_file": {
        "function": create_file,
        "description": "在某个目录下新建1个文件，并且写入内容",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                },
                "content": {
                    "type": "string",
                    "description": "文件内容"
                }
            },
            "required": ["directory", "filename", "content"]
        }
    },
    "read_file": {
        "function": read_file,
        "description": "读取某个目录下的某个文件的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "目录路径"
                },
                "filename": {
                    "type": "string",
                    "description": "文件名"
                }
            },
            "required": ["directory", "filename"]
        }
    },
    "search_internet": {
        "function": search_internet,
        "description": "根据用户对话的内容搜索互联网",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索查询词"
                }
            },
            "required": ["query"]
        }
    },
    "anythingllm_query": {
        "function": anythingllm_query,
        "description": "访问AnythingLLM的聊天API接口，查询文档仓库中的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "查询内容"
                }
            },
            "required": ["query"]
        }
    }
}
