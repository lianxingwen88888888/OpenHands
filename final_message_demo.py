#!/usr/bin/env python3
"""
Final comprehensive demo showing OpenHands message structure.
This shows exactly what messages look like when sent to the LLM.
"""

import json
from openhands.core.message import Message, TextContent


def show_openhands_messages():
    """Show the actual message structure used in OpenHands."""
    
    print("=" * 80)
    print("OPENHANDS MESSAGES - WHAT GETS SENT TO THE LLM")
    print("=" * 80)
    
    # This is what the actual messages array looks like
    messages = [
        # 1. System message
        Message(
            role='system',
            content=[TextContent(text="You are OpenHands agent, a helpful AI assistant that can interact with a computer to solve tasks. You have access to tools like execute_bash, str_replace_editor, and browser.")]
        ),
        
        # 2. User message
        Message(
            role='user',
            content=[TextContent(text="Hello! Can you help me create a Python script?")]
        ),
        
        # 3. Assistant response
        Message(
            role='assistant',
            content=[TextContent(text="I'll help you create a Python script. What would you like the script to do?")]
        ),
        
        # 4. User specification
        Message(
            role='user',
            content=[TextContent(text="Create a script that prints Hello World")]
        ),
        
        # 5. Assistant action plan
        Message(
            role='assistant',
            content=[TextContent(text="I'll create a simple Python script that prints 'Hello World' for you.")]
        ),
        
        # 6. Tool response (file creation result)
        Message(
            role='tool',
            content=[TextContent(text="File created successfully: hello.py\n\nContent:\nprint('Hello World')")],
            tool_call_id="call_123",
            name="str_replace_editor"
        ),
        
        # 7. Assistant completion
        Message(
            role='assistant',
            content=[TextContent(text="Perfect! I've created a Python script called 'hello.py' that prints 'Hello World'. You can run it with: python hello.py")]
        )
    ]
    
    return messages


def print_messages_detail(messages):
    """Print detailed information about each message."""
    
    print(f"\n📋 CONVERSATION DETAILS:")
    print(f"Total messages: {len(messages)}")
    print(f"Message roles: {[msg.role for msg in messages]}")
    
    for i, msg in enumerate(messages, 1):
        print(f"\n--- MESSAGE {i} ---")
        print(f"Role: {msg.role}")
        
        # Show tool information if present
        if msg.tool_call_id:
            print(f"Tool Call ID: {msg.tool_call_id}")
            print(f"Tool Name: {msg.name}")
        
        # Show content
        for j, content in enumerate(msg.content):
            if isinstance(content, TextContent):
                text_preview = content.text[:100] + "..." if len(content.text) > 100 else content.text
                print(f"Content: {text_preview}")
        
        # Show serialized JSON
        serialized = msg.model_dump()
        print(f"JSON: {json.dumps(serialized, indent=2)}")


def show_message_flow():
    """Show how messages flow in the conversation."""
    
    print("\n" + "=" * 80)
    print("MESSAGE FLOW EXPLANATION")
    print("=" * 80)
    
    flow_explanation = [
        ("SYSTEM", "Sets up the agent with instructions and available tools"),
        ("USER", "Initial request from human user"),
        ("ASSISTANT", "Agent acknowledges and asks for clarification"),
        ("USER", "User provides specific requirements"),
        ("ASSISTANT", "Agent explains what it will do"),
        ("TOOL", "Result of tool execution (file creation)"),
        ("ASSISTANT", "Agent confirms completion and provides usage instructions")
    ]
    
    for i, (role, explanation) in enumerate(flow_explanation, 1):
        print(f"{i}. {role:10} → {explanation}")
    
    print(f"\nThis creates a conversation of {len(flow_explanation)} messages that the LLM processes.")


def show_key_concepts():
    """Show key concepts about OpenHands messages."""
    
    print("\n" + "=" * 80)
    print("KEY CONCEPTS")
    print("=" * 80)
    
    concepts = [
        "Messages follow OpenAI chat completion format",
        "Four roles: 'system', 'user', 'assistant', 'tool'",
        "System message contains agent instructions and available tools",
        "User messages contain human requests",
        "Assistant messages contain agent responses and reasoning",
        "Tool messages contain results of executed actions",
        "Each message has content as a list of TextContent/ImageContent",
        "Tool messages include tool_call_id and tool name",
        "ConversationMemory.process_events() converts events to messages",
        "The entire messages array is sent to LLM for context"
    ]
    
    for i, concept in enumerate(concepts, 1):
        print(f"{i:2d}. {concept}")


def show_actual_json():
    """Show what the actual JSON looks like when sent to LLM."""
    
    print("\n" + "=" * 80)
    print("ACTUAL JSON SENT TO LLM")
    print("=" * 80)
    
    # Simple example of what gets sent
    example_payload = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "system",
                "content": "You are OpenHands agent, a helpful AI assistant..."
            },
            {
                "role": "user", 
                "content": "Create a Python script"
            },
            {
                "role": "assistant",
                "content": "I'll create a Python script for you."
            },
            {
                "role": "tool",
                "content": "File created: script.py",
                "tool_call_id": "call_123",
                "name": "str_replace_editor"
            },
            {
                "role": "assistant",
                "content": "Script created successfully!"
            }
        ],
        "temperature": 0.1,
        "max_tokens": 4096
    }
    
    print("Example API payload:")
    print(json.dumps(example_payload, indent=2))


if __name__ == "__main__":
    print("OpenHands Message Structure - Complete Guide")
    print("This shows exactly what messages look like in OpenHands")
    
    # Get the messages
    messages = show_openhands_messages()
    
    # Show detailed breakdown
    print_messages_detail(messages)
    
    # Show message flow
    show_message_flow()
    
    # Show key concepts
    show_key_concepts()
    
    # Show actual JSON
    show_actual_json()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("✅ OpenHands converts events (actions/observations) into messages")
    print("✅ Messages follow standard chat completion format")
    print("✅ ConversationMemory.process_events() is the key conversion method")
    print("✅ The messages array provides full context to the LLM")
    print("✅ Tool calls create request-response patterns in the conversation")
    print("✅ Each message type serves a specific purpose in the conversation flow")
    
    print(f"\n🎯 In this example, {len(messages)} messages would be sent to the LLM")
    print("   The LLM uses this entire context to generate its next response.")