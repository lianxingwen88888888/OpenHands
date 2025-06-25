#!/usr/bin/env python3
"""
Simple demo to show OpenHands message structure without complex function calling.
This demonstrates what the actual messages look like when sent to the LLM.
"""

import json
from typing import Any

from openhands.core.message import Message, TextContent, ImageContent


def demonstrate_message_structure():
    """Show the actual message structure used in OpenHands."""
    
    print("=" * 80)
    print("OPENHANDS MESSAGE STRUCTURE EXAMPLES")
    print("=" * 80)
    
    # 1. System message (sets up the agent)
    system_msg = Message(
        role='system',
        content=[TextContent(text="""You are OpenHands, an AI assistant that can help with software development tasks.

You have access to the following tools:
- execute_bash: Run bash commands
- str_replace_editor: Edit files
- browser: Browse the web

Always think step by step and explain your reasoning.""")]
    )
    
    print("\n1. SYSTEM MESSAGE (Agent Setup):")
    print(f"   Role: {system_msg.role}")
    print(f"   Content: {system_msg.content[0].text[:100]}...")
    print(f"   Serialized JSON:")
    print(json.dumps(system_msg.model_dump(), indent=2))
    
    # 2. User message
    user_msg = Message(
        role='user',
        content=[TextContent(text="Hello! Can you help me create a simple Python script that prints 'Hello World'?")]
    )
    
    print("\n2. USER MESSAGE:")
    print(f"   Role: {user_msg.role}")
    print(f"   Content: {user_msg.content[0].text}")
    print(f"   Serialized JSON:")
    print(json.dumps(user_msg.model_dump(), indent=2))
    
    # 3. Assistant message with reasoning
    assistant_msg = Message(
        role='assistant',
        content=[TextContent(text="""I'll help you create a simple Python script that prints 'Hello World'. Let me create this file for you.

I'll use the str_replace_editor tool to create a new Python file.""")]
    )
    
    print("\n3. ASSISTANT MESSAGE (with reasoning):")
    print(f"   Role: {assistant_msg.role}")
    print(f"   Content: {assistant_msg.content[0].text}")
    print(f"   Serialized JSON:")
    print(json.dumps(assistant_msg.model_dump(), indent=2))
    
    # 4. Tool response message (result of executing a command)
    tool_response = Message(
        role='tool',
        content=[TextContent(text="""File created successfully at: /workspace/hello.py

Content:
```python
print("Hello World")
```""")],
        tool_call_id="call_abc123",
        name="str_replace_editor"
    )
    
    print("\n4. TOOL RESPONSE MESSAGE:")
    print(f"   Role: {tool_response.role}")
    print(f"   Content: {tool_response.content[0].text}")
    print(f"   Tool call ID: {tool_response.tool_call_id}")
    print(f"   Tool name: {tool_response.name}")
    print(f"   Serialized JSON:")
    print(json.dumps(tool_response.model_dump(), indent=2))
    
    # 5. User message with image (vision capability)
    vision_msg = Message(
        role='user',
        content=[
            TextContent(text="I have a screenshot of an error. Can you help me debug it?"),
            ImageContent(image_urls=["data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="])
        ],
        vision_enabled=True
    )
    
    print("\n5. USER MESSAGE WITH IMAGE (Vision):")
    print(f"   Role: {vision_msg.role}")
    print(f"   Text content: {vision_msg.content[0].text}")
    print(f"   Image URLs: {len(vision_msg.content[1].image_urls)} image(s)")
    print(f"   Vision enabled: {vision_msg.vision_enabled}")
    print(f"   Contains image: {vision_msg.contains_image}")
    print(f"   Serialized JSON:")
    print(json.dumps(vision_msg.model_dump(), indent=2))
    
    # 6. Multiple consecutive user messages (with formatting)
    user_msg1 = Message(
        role='user',
        content=[TextContent(text="First message")]
    )
    
    user_msg2 = Message(
        role='user',
        content=[TextContent(text="\n\nSecond message (note the newlines for separation)")]
    )
    
    print("\n6. CONSECUTIVE USER MESSAGES (with formatting):")
    print("   Message 1:")
    print(f"     Content: '{user_msg1.content[0].text}'")
    print("   Message 2:")
    print(f"     Content: '{user_msg2.content[0].text}'")
    print("   (OpenHands adds double newlines between consecutive user messages)")


def show_conversation_flow():
    """Show how messages flow in a typical OpenHands conversation."""
    
    print("\n" + "=" * 80)
    print("TYPICAL CONVERSATION FLOW")
    print("=" * 80)
    
    conversation = [
        {
            "role": "system",
            "content": "You are OpenHands, an AI assistant...",
            "description": "Sets up the agent with instructions and available tools"
        },
        {
            "role": "user", 
            "content": "Create a Python script that calculates fibonacci numbers",
            "description": "User's initial request"
        },
        {
            "role": "assistant",
            "content": "I'll create a Python script for fibonacci calculations. Let me start by creating the file.",
            "description": "Agent acknowledges and plans the task"
        },
        {
            "role": "tool",
            "content": "File created: fibonacci.py\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "description": "Tool execution result (file creation)"
        },
        {
            "role": "assistant",
            "content": "I've created a fibonacci.py script with a recursive implementation. Would you like me to add a main function to test it?",
            "description": "Agent reports completion and asks for next steps"
        },
        {
            "role": "user",
            "content": "Yes, please add a main function that prints the first 10 fibonacci numbers",
            "description": "User provides additional requirements"
        },
        {
            "role": "assistant",
            "content": "I'll add a main function to print the first 10 fibonacci numbers.",
            "description": "Agent acknowledges the new request"
        },
        {
            "role": "tool",
            "content": "File updated: fibonacci.py\n\nAdded main function:\nif __name__ == '__main__':\n    for i in range(10):\n        print(f'F({i}) = {fibonacci(i)}')",
            "description": "Tool execution result (file update)"
        },
        {
            "role": "assistant",
            "content": "Perfect! I've updated the script with a main function. The script now calculates and prints the first 10 fibonacci numbers when run.",
            "description": "Agent confirms completion"
        }
    ]
    
    print("\nConversation Flow:")
    for i, msg in enumerate(conversation, 1):
        print(f"\n{i}. {msg['role'].upper()} MESSAGE:")
        print(f"   Content: {msg['content'][:80]}{'...' if len(msg['content']) > 80 else ''}")
        print(f"   Purpose: {msg['description']}")
    
    print(f"\nTotal messages: {len(conversation)}")
    print("Roles distribution:", {role: sum(1 for msg in conversation if msg['role'] == role) for role in set(msg['role'] for msg in conversation)})


def show_message_serialization():
    """Show how messages are serialized for different LLM providers."""
    
    print("\n" + "=" * 80)
    print("MESSAGE SERIALIZATION FOR DIFFERENT PROVIDERS")
    print("=" * 80)
    
    # Create a sample message
    msg = Message(
        role='user',
        content=[
            TextContent(text="Hello, can you help me?"),
            ImageContent(image_urls=["data:image/png;base64,abc123"])
        ]
    )
    
    print("\nSample message with text and image:")
    print(f"Role: {msg.role}")
    print(f"Content items: {len(msg.content)}")
    print(f"Contains image: {msg.contains_image}")
    
    # String serialization (for providers without vision support)
    msg.force_string_serializer = True
    string_format = msg.model_dump()
    print(f"\n1. STRING FORMAT (for basic providers):")
    print(json.dumps(string_format, indent=2))
    
    # List serialization (for providers with vision support)
    msg.force_string_serializer = False
    msg.vision_enabled = True
    list_format = msg.model_dump()
    print(f"\n2. LIST FORMAT (for vision-enabled providers):")
    print(json.dumps(list_format, indent=2))


if __name__ == "__main__":
    print("OpenHands Message Structure Demo")
    print("This shows the actual message format sent to LLMs")
    
    demonstrate_message_structure()
    show_conversation_flow()
    show_message_serialization()
    
    print("\n" + "=" * 80)
    print("KEY POINTS ABOUT OPENHANDS MESSAGES:")
    print("=" * 80)
    print("1. Messages follow OpenAI's chat completion format")
    print("2. Four main roles: 'system', 'user', 'assistant', 'tool'")
    print("3. Content can be text-only or include images (vision)")
    print("4. Tool calls and responses are handled via special message types")
    print("5. Messages are serialized differently based on provider capabilities")
    print("6. Conversation memory processes events into this message format")
    print("7. The ConversationMemory.process_events() method is the key converter")