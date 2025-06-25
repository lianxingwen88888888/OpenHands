#!/usr/bin/env python3
"""
Script to log actual OpenHands messages sent to LLM.
Add this to ConversationMemory to see real messages.
"""

import json
import os
from datetime import datetime
from typing import Any

def log_messages_to_file(messages: list, filename: str = None):
    """Log messages array to a file for inspection."""
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openhands_messages_{timestamp}.json"
    
    # Create logs directory if it doesn't exist
    log_dir = "/tmp/openhands_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, filename)
    
    # Convert messages to serializable format
    serializable_messages = []
    for msg in messages:
        if hasattr(msg, 'model_dump'):
            serializable_messages.append(msg.model_dump())
        else:
            serializable_messages.append(str(msg))
    
    # Create log entry
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "total_messages": len(messages),
        "message_roles": [msg.get('role', 'unknown') if isinstance(msg, dict) else getattr(msg, 'role', 'unknown') for msg in messages],
        "messages": serializable_messages
    }
    
    # Write to file
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)
    
    print(f"Messages logged to: {log_file}")
    return log_file

# Patch to add to ConversationMemory.process_events()
PATCH_CODE = '''
# Add this to the end of ConversationMemory.process_events() method
# Right before "return messages"

# Log messages for debugging
try:
    from log_messages import log_messages_to_file
    log_messages_to_file(messages)
except Exception as e:
    logger.debug(f"Failed to log messages: {e}")

return messages
'''

def create_patch_instructions():
    """Create instructions for patching OpenHands to log messages."""
    
    instructions = """
# 如何记录真实的OpenHands messages

## 方法1: 修改ConversationMemory类

在 `openhands/memory/conversation_memory.py` 的 `process_events` 方法末尾添加：

```python
# 在 return messages 之前添加
import json
import os
from datetime import datetime

# Log messages for debugging  
try:
    log_dir = "/tmp/openhands_logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"messages_{timestamp}.json")
    
    # Convert to serializable format
    serializable_messages = [msg.model_dump() for msg in messages]
    
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "total_messages": len(messages),
        "messages": serializable_messages
    }
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
        
    print(f"🔍 Messages logged to: {log_file}")
    
except Exception as e:
    print(f"Failed to log messages: {e}")
```

## 方法2: 使用环境变量控制

```python
# 在process_events方法中添加
if os.getenv('OPENHANDS_LOG_MESSAGES', 'false').lower() == 'true':
    # 记录messages的代码
```

然后运行时设置：
```bash
export OPENHANDS_LOG_MESSAGES=true
```

## 方法3: 修改LLM调用处

在 `openhands/llm/` 相关文件中，在调用LLM API之前记录messages。

## 查看日志

日志会保存在 `/tmp/openhands_logs/` 目录下，包含：
- 完整的messages数组
- 每个message的详细结构
- 时间戳和统计信息
"""
    
    return instructions

if __name__ == "__main__":
    print("OpenHands Messages Logger")
    print("=" * 50)
    
    print(create_patch_instructions())
    
    print("\n" + "=" * 50)
    print("注意：我作为Claude无法直接访问发送给我的messages")
    print("你需要修改OpenHands代码来记录真实的messages数组")
    print("=" * 50)