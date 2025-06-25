# OpenHands LLM交互记录系统

## 概述

这个功能为OpenHands添加了完整的LLM交互记录能力，可以记录：
- ConversationMemory生成的messages数组
- 发送给LLM的完整请求
- LLM返回的完整响应
- 请求参数、延迟、token使用等元数据

## 功能特性

### 🔍 完整的交互记录
- ✅ 记录每次ConversationMemory.process_events()生成的messages
- ✅ 记录每次LLM API调用的请求和响应
- ✅ 包含时间戳、延迟、token使用等详细信息
- ✅ 支持工具调用(function calling)的记录

### 📊 丰富的元数据
- 模型信息和配置参数
- 消息角色分布统计
- 请求响应延迟测量
- Token使用量统计
- 工具调用详细信息

### 🛠️ 便捷的工具
- 自动日志记录（无需手动配置）
- 多种查看和分析工具
- 测试和演示脚本
- 详细的使用文档

## 修改的核心文件

### 1. `openhands/memory/conversation_memory.py`
在`process_events()`方法中添加了messages记录功能：
- 记录生成的完整messages数组
- 统计消息角色分布
- 分析消息内容类型
- 保存到`/tmp/openhands_logs/real_messages_*.json`

### 2. `openhands/llm/llm.py`
在LLM wrapper函数中添加了完整的请求-响应记录：
- 记录发送给LLM的messages
- 记录LLM返回的response
- 包含请求参数和元数据
- 保存到`/tmp/openhands_logs/llm_interaction_*.json`

## 工具脚本

### 核心工具
- `trigger_message_logging.py` - 触发ConversationMemory记录
- `test_direct_llm_logging.py` - 测试LLM交互记录
- `view_llm_interactions.py` - 查看所有记录的交互
- `show_real_messages.py` - 显示messages数组

### 演示脚本
- `demo_messages.py` - 基础演示
- `simple_message_demo.py` - 简单示例
- `final_message_demo.py` - 完整演示
- `real_conversation_example.py` - 真实对话示例

### 文档
- `COMPLETE_LLM_LOGGING_GUIDE.md` - 完整使用指南
- `OPENHANDS_MESSAGES_EXPLAINED.md` - Messages结构详解
- `LLM_INTERACTION_LOGGING_README.md` - 本文档

## 使用方法

### 1. 查看现有记录
```bash
python view_llm_interactions.py
```

### 2. 触发新的记录
```bash
# 测试ConversationMemory
python trigger_message_logging.py

# 测试LLM交互
python test_direct_llm_logging.py
```

### 3. 查看日志文件
```bash
ls -la /tmp/openhands_logs/
```

## 日志文件格式

### ConversationMemory Messages
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
      "role": "system"
    }
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
  "messages": [...],
  "response": {
    "response_timestamp": "2025-06-25T11:01:58.213326",
    "latency_seconds": 0.5,
    "response_content": "Hello! This is a response.",
    "raw_response": {
      "choices": [...],
      "usage": {
        "prompt_tokens": 25,
        "completion_tokens": 15,
        "total_tokens": 40
      }
    }
  }
}
```

## 实际应用

### 在真实OpenHands中
当运行真实的OpenHands实例时：
1. 每次ConversationMemory处理事件时自动记录
2. 每次LLM API调用时自动记录
3. 所有日志保存到`/tmp/openhands_logs/`
4. 可以实时查看OpenHands与LLM的完整交互

### 调试和分析
- 查看OpenHands如何构建messages
- 分析LLM的响应模式
- 监控token使用和性能
- 调试对话流程问题

## 技术实现

### 日志记录策略
- 非侵入式：不影响原有功能
- 异常安全：记录失败不影响主流程
- 性能友好：最小化性能影响
- 结构化：JSON格式便于分析

### 文件命名规则
- `real_messages_YYYYMMDD_HHMMSS_mmm.json` - ConversationMemory记录
- `llm_interaction_YYYYMMDD_HHMMSS_mmm.json` - LLM交互记录

## 示例输出

### 真实的Messages数组
```json
[
  {
    "role": "system",
    "content": "You are OpenHands agent, a helpful AI assistant..."
  },
  {
    "role": "user",
    "content": "Hello! Can you help me create a Python script?"
  },
  {
    "role": "assistant",
    "content": "I'll help you create a Python script..."
  },
  {
    "role": "tool",
    "content": "File created successfully...",
    "tool_call_id": "call_123",
    "name": "str_replace_editor"
  }
]
```

## 总结

这个系统提供了OpenHands与LLM交互的完全透明度，让你能够：
- 🔍 深入了解OpenHands的内部工作机制
- 📊 分析对话模式和性能指标
- 🐛 调试和优化对话流程
- 📈 监控LLM使用情况

所有功能都是自动的，无需手动配置，为OpenHands的开发和调试提供了强大的工具。