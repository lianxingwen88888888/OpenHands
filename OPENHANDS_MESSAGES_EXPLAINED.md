# OpenHands Messages Structure - Complete Guide

This document explains exactly what the `messages` array looks like in OpenHands when it's sent to the LLM. This is the result of the `ConversationMemory.process_events()` method that you asked about.

## Overview

OpenHands converts **Events** (Actions and Observations) into **Messages** that follow the OpenAI chat completion format. The `ConversationMemory.process_events()` method is responsible for this conversion.

## Message Structure

Each message in the array has this structure:

```python
Message(
    role: Literal['user', 'system', 'assistant', 'tool'],
    content: list[TextContent | ImageContent],
    tool_call_id: str | None = None,  # For tool responses
    name: str | None = None,          # Tool name for tool responses
    tool_calls: list[ToolCall] | None = None  # For function calling
)
```

## The Four Message Roles

### 1. `system` - Agent Setup
- **Purpose**: Sets up the agent with instructions and available tools
- **Source**: `SystemMessageAction` events
- **Example**:
```json
{
  "role": "system",
  "content": "You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks. You have access to tools like execute_bash, str_replace_editor, and browser."
}
```

### 2. `user` - Human Requests
- **Purpose**: Contains requests and messages from the human user
- **Source**: `MessageAction` events with `source='user'`
- **Example**:
```json
{
  "role": "user",
  "content": "Hello! Can you help me create a Python script?"
}
```

### 3. `assistant` - Agent Responses
- **Purpose**: Contains the agent's responses, reasoning, and plans
- **Source**: `MessageAction` events with `source='agent'`
- **Example**:
```json
{
  "role": "assistant",
  "content": "I'll help you create a Python script. What would you like the script to do?"
}
```

### 4. `tool` - Tool Execution Results
- **Purpose**: Contains the results of tool executions (bash commands, file operations, etc.)
- **Source**: Various `Observation` events (CmdOutputObservation, FileEditObservation, etc.)
- **Example**:
```json
{
  "role": "tool",
  "content": "File created successfully: hello.py\n\nContent:\nprint('Hello World')",
  "tool_call_id": "call_123",
  "name": "str_replace_editor"
}
```

## Real Conversation Example

Here's what a typical OpenHands conversation looks like as messages:

```python
messages = [
    # 1. System setup
    {
        "role": "system",
        "content": "You are OpenHands agent, a helpful AI assistant..."
    },
    
    # 2. User request
    {
        "role": "user",
        "content": "Create a Python script that prints Hello World"
    },
    
    # 3. Agent acknowledgment
    {
        "role": "assistant", 
        "content": "I'll create a simple Python script for you."
    },
    
    # 4. Tool execution result
    {
        "role": "tool",
        "content": "File created: hello.py\nprint('Hello World')",
        "tool_call_id": "call_123",
        "name": "str_replace_editor"
    },
    
    # 5. Agent completion
    {
        "role": "assistant",
        "content": "Perfect! I've created hello.py. Run it with: python hello.py"
    }
]
```

## Content Types

Messages can contain different types of content:

### TextContent
```python
TextContent(text="Your message here")
```

### ImageContent (for vision)
```python
ImageContent(image_urls=["data:image/png;base64,..."])
```

### Mixed Content Example
```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "What do you see in this image?"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "data:image/png;base64,..."
      }
    }
  ]
}
```

## How Events Become Messages

The `ConversationMemory.process_events()` method converts OpenHands events:

1. **SystemMessageAction** → `system` message
2. **MessageAction (user)** → `user` message  
3. **MessageAction (agent)** → `assistant` message
4. **CmdRunAction** → Creates tool call (function calling mode)
5. **CmdOutputObservation** → `tool` message with results
6. **FileEditAction** → Creates tool call
7. **FileEditObservation** → `tool` message with results

## Function Calling vs Non-Function Calling

### Function Calling Mode (Default)
- Agent actions create tool calls in assistant messages
- Tool results become separate `tool` messages
- More structured conversation flow

### Non-Function Calling Mode
- Actions become regular assistant messages
- Observations become user messages
- Simpler but less structured

## Message Serialization

Messages are serialized differently based on LLM capabilities:

### String Format (Basic providers)
```json
{
  "role": "user",
  "content": "Hello, can you help me?"
}
```

### List Format (Vision-enabled providers)
```json
{
  "role": "user", 
  "content": [
    {"type": "text", "text": "Hello, can you help me?"},
    {"type": "image_url", "image_url": {"url": "..."}}
  ]
}
```

## Key Processing Rules

1. **System Message First**: Always starts with a system message
2. **User Message Second**: Ensures conversation starts with user input
3. **Tool Call Matching**: Tool calls are matched with their responses
4. **Message Formatting**: Consecutive user messages get double newlines
5. **Content Truncation**: Long observations are truncated based on `max_message_chars`
6. **Vision Handling**: Images included only when `vision_is_active=True`

## API Payload Example

This is what actually gets sent to the LLM API:

```json
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are OpenHands agent..."},
    {"role": "user", "content": "Create a Python script"},
    {"role": "assistant", "content": "I'll create a script for you."},
    {"role": "tool", "content": "File created: script.py", "tool_call_id": "call_123", "name": "str_replace_editor"},
    {"role": "assistant", "content": "Script created successfully!"}
  ],
  "temperature": 0.1,
  "max_tokens": 4096
}
```

## Summary

- **Input**: List of Events (Actions and Observations)
- **Process**: `ConversationMemory.process_events()`
- **Output**: List of Messages in chat completion format
- **Purpose**: Provide structured conversation context to the LLM
- **Result**: LLM generates next response based on full message history

The messages array is the bridge between OpenHands' event-driven architecture and the LLM's chat-based interface. Every interaction you have with OpenHands gets converted into this structured format before being sent to the language model.