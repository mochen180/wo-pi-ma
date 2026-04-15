# AI智能体开发教学项目

## 项目结构

```
project1/
├── practice01/          # 练习目录1 - 基础LLM调用
│   └── llm_client.py     # LLM客户端代码
├── practice02/          # 练习目录2 - 交互式聊天
│   └── chat_client.py    # 交互式聊天客户端
├── venv/               # 虚拟环境
├── .env                # 环境配置文件（用户创建）
├── .env.example        # 环境配置示例
├── .gitignore          # Git忽略文件
└── README.md           # 项目说明
```

## 代码功能说明

### practice01/llm_client.py

**功能用途：**
1. **环境变量加载**：从项目根目录的`.env`文件读取配置信息
2. **LLM API调用**：使用Python标准HTTP库调用OpenAI兼容协议的LLM服务
3. **性能统计**：
   - 统计token消耗（输入、输出、总token数）
   - 计算响应时间
   - 计算token处理速度（tokens/s）
4. **错误处理**：处理网络连接、API响应等各种错误情况

**核心功能：**
- `load_env()`: 加载并解析.env文件中的配置
- `call_llm(prompt, env_vars)`: 调用LLM API并返回结果和统计信息

**默认配置：**
- BASE_URL: http://127.0.0.1:1234（本地模型默认地址）
- MODEL: qwen3.5-4b（默认模型）
- API_KEY: qwen3.5-4b（默认API密钥）
- MAX_TOKENS: 1000
- TEMPERATURE: 0.7

### practice02/chat_client.py

**功能用途：**
1. **交互式聊天**：支持在终端中输入聊天信息
2. **流式输出**：实时显示AI的响应，模拟真实对话体验
3. **历史记录**：自动将历史聊天记录添加到上下文，保持对话连贯性
4. **持续对话**：循环运行直到用户按Ctrl+C退出
5. **性能统计**：每次对话后显示token消耗和性能指标

**核心功能：**
- `load_env()`: 加载并解析.env文件中的配置
- `call_llm_stream(prompt, env_vars, messages)`: 流式调用LLM API并实时显示响应

**默认配置：**
- BASE_URL: http://127.0.0.1:1234（本地模型默认地址）
- MODEL: qwen3.5-4b（默认模型）
- API_KEY: qwen3.5-4b（默认API密钥）
- MAX_TOKENS: 1000
- TEMPERATURE: 0.7

## 教学目标

### Practice 01 - 基础LLM调用

1. **Python基础**：
   - 文件操作（读取.env文件）
   - 异常处理
   - 模块导入和使用

2. **网络编程**：
   - 使用标准库`http.client`进行HTTP请求
   - URL解析和处理
   - 请求头设置和认证

3. **API调用**：
   - 理解OpenAI兼容协议的API结构
   - 构建正确的请求数据
   - 解析API响应

4. **性能分析**：
   - 时间计算和性能统计
   - Token消耗分析
   - 速度计算

5. **配置管理**：
   - 环境变量配置
   - 配置文件使用

6. **错误处理**：
   - 网络错误处理
   - API错误处理
   - 配置错误处理

### Practice 02 - 交互式聊天

1. **流式API调用**：
   - 理解流式响应的工作原理
   - 实时处理和显示流式数据
   - 处理SSE（Server-Sent Events）格式

2. **交互式界面**：
   - 终端输入输出处理
   - 用户输入捕获
   - 实时响应显示

3. **对话管理**：
   - 维护聊天历史记录
   - 上下文管理和传递
   - 历史记录长度控制

4. **事件处理**：
   - 键盘中断处理（Ctrl+C退出）
   - 异常捕获和处理
   - 优雅退出机制

5. **用户体验**：
   - 实时响应反馈
   - 清晰的界面提示
   - 性能指标展示

## 使用方法

### Practice 01 - 基础LLM调用

1. **配置环境**：
   - 复制`env.example`为`.env`
   - 填写正确的API配置信息

2. **运行测试**：
   ```bash
   cd practice01
   python llm_client.py
   ```

3. **查看结果**：
   - LLM的响应内容
   - Token使用统计
   - 性能指标

### Practice 02 - 交互式聊天

1. **配置环境**：
   - 使用与practice01相同的`.env`配置

2. **运行聊天客户端**：
   ```bash
   cd practice02
   python chat_client.py
   ```

3. **使用方法**：
   - 在终端中输入消息并按回车
   - 观察AI的实时流式响应
   - 继续输入新的问题，系统会保持对话上下文
   - 按Ctrl+C退出聊天

4. **查看结果**：
   - 实时的AI响应
   - 每次对话后的性能统计
   - 持续的对话历史

## 支持的LLM服务

- **本地模型**：通过Ollama等工具部署的本地模型
- **国内服务**：智谱AI、百川智能等OpenAI兼容服务
- **OpenAI官方**：需要网络访问权限

## 扩展建议

1. 添加更多API参数支持
2. 实现批量请求功能
3. 添加缓存机制
4. 支持流式响应
5. 实现不同模型的适配

## 技术栈

- Python 3.11+
- 标准库：os, json, time, http.client, urllib.parse
- 无第三方依赖

## 注意事项

- 确保`.env`文件中的API密钥安全，不要提交到版本控制系统
- 对于本地模型，需要先启动模型服务
- 不同LLM服务的API格式可能略有差异，需要根据实际情况调整配置