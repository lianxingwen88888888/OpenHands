# OpenHands 完整LLM交互记录指南

## 概述

我已经为你修改了OpenHands代码，现在可以记录：
1. **ConversationMemory.process_events()** 生成的messages数组
2. **LLM.completion()** 的完整请求-响应交互

## 修改的文件

### 1. `/workspace/OpenHands/openhands/memory/conversation_memory.py`
- 在 `process_events()` 方法末尾添加了日志记录
- 记录每次生成的messages数组
- 文件保存在 `/tmp/openhands_logs/real_messages_*.json`

### 2. `/workspace/OpenHands/openhands/llm/llm.py`
- 在LLM wrapper函数中添加了完整的请求-响应记录
- 记录发送给LLM的messages和LLM返回的response
- 文件保存在 `/tmp/openhands_logs/llm_interaction_*.json`

## 记录的数据结构

### ConversationMemory Messages 记录
```json
{
  "timestamp": "2025-06-25T09:21:47.754789",
  "session_info": "Real OpenHands conversation messages",
  "total_messages": 3,
  "message_roles": ["system", "user", "assistant"],
  "role_distribution": {"system": 1, "user": 1, "assistant": 1},
  "messages": [
    {
      "content": "You are OpenHands, an AI assistant.",
      "role": "system",
      "_debug_info": {
        "contains_image": false,
        "content_count": 1,
        "content_types": ["TextContent"]
      }
    }
    // ... 更多消息
  ]
}
```

### LLM交互记录
```json
{
  "timestamp": "2025-06-25T11:01:58.208394",
  "interaction_type": "COMPLETE_LLM_INTERACTION",
  "model": "gpt-3.5-turbo",
  "total_messages": 2,
  "message_roles": ["system", "user"],
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant for testing logging."
    },
    {
      "role": "user", 
      "content": "This is a test message to verify our logging system works correctly."
    }
  ],
  "kwargs": {
    "max_tokens": 100,
    "temperature": 0.1
  },
  "function_calling_active": false,
  "mock_function_calling": true,
  "response": {
    "response_timestamp": "2025-06-25T11:01:58.213326",
    "latency_seconds": 0.5,
    "response_id": "mock_response_123",
    "response_content": "Hello! This is a mock response for testing the logging functionality.",
    "tool_calls": [],
    "raw_response": {
      "choices": [
        {
          "message": {
            "role": "assistant",
            "content": "Hello! This is a mock response for testing the logging functionality.",
            "tool_calls": null
          },
          "finish_reason": "stop"
        }
      ],
      "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 15,
        "total_tokens": 40
      }
    }
  }
}
```

## 创建的工具脚本

### 1. `trigger_message_logging.py`
- 触发ConversationMemory记录
- 测试messages数组生成

### 2. `test_direct_llm_logging.py`
- 直接测试LLM交互记录
- 创建模拟的完整交互

### 3. `view_llm_interactions.py`
- 查看所有记录的交互
- 显示详细的请求-响应信息

### 4. `show_real_messages.py`
- 显示ConversationMemory生成的messages

## 如何使用

### 查看现有记录
```bash
cd /workspace/OpenHands
python view_llm_interactions.py
```

### 触发新的记录
```bash
# 测试ConversationMemory
python trigger_message_logging.py

# 测试LLM交互
python test_direct_llm_logging.py
```

### 查看日志文件
```bash
ls -la /tmp/openhands_logs/
```

## 日志文件位置

所有日志保存在 `/tmp/openhands_logs/` 目录下：

- `real_messages_*.json` - ConversationMemory生成的messages
- `llm_interaction_*.json` - 完整的LLM请求-响应交互

## 记录的信息包括

### Messages数组记录
- ✅ 每个message的role、content
- ✅ 消息类型（TextContent/ImageContent）
- ✅ 工具调用信息（tool_call_id, name）
- ✅ 时间戳和统计信息

### LLM交互记录
- ✅ 发送给LLM的完整messages数组
- ✅ LLM返回的完整response
- ✅ 请求参数（temperature, max_tokens等）
- ✅ 响应延迟和token使用情况
- ✅ 工具调用的详细信息
- ✅ 函数调用模式信息

## 在真实OpenHands中的使用

当你运行真实的OpenHands实例时：

1. 每次 `ConversationMemory.process_events()` 被调用时，都会记录生成的messages
2. 每次LLM API调用时，都会记录完整的请求-响应
3. 所有日志自动保存到 `/tmp/openhands_logs/`
4. 你可以实时查看OpenHands与LLM的完整交互过程

## 示例：真实的Messages数组

这是一个真实的OpenHands messages数组示例：

```json
[
  {
    "role": "system",
    "content": "You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks. You have access to tools like execute_bash, str_replace_editor, and browser."
  },
  {
    "role": "user",
    "content": "Hello! Can you help me create a Python script?"
  },
  {
    "role": "assistant",
    "content": "I'll help you create a Python script. What would you like the script to do?"
  },
  {
    "role": "user",
    "content": "Create a script that prints Hello World"
  },
  {
    "role": "assistant",
    "content": "I'll create a simple Python script that prints 'Hello World' for you."
  },
  {
    "role": "tool",
    "content": "File created successfully: hello.py\n\nContent:\nprint('Hello World')",
    "tool_call_id": "call_123",
    "name": "str_replace_editor"
  },
  {
    "role": "assistant",
    "content": "Perfect! I've created a Python script called 'hello.py' that prints 'Hello World'. You can run it with: python hello.py"
  }
]
```

## 总结

现在你可以完全看到：
- 🔍 OpenHands如何将事件转换为messages
- 🔍 发送给LLM的确切messages数组
- 🔍 LLM返回的完整response
- 🔍 整个对话的完整流程

这些日志记录让你能够深入了解OpenHands的内部工作机制！