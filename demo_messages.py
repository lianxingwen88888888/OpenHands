#!/usr/bin/env python3
"""
Demo script to show the structure of messages in OpenHands conversation memory.
This demonstrates what the actual messages look like when sent to the LLM.
"""

import json
from typing import Any

from openhands.core.config.agent_config import AgentConfig
from openhands.core.message import Message, TextContent, ImageContent
from openhands.events.action import MessageAction, CmdRunAction, SystemMessageAction
from openhands.events.observation import CmdOutputObservation
from openhands.memory.conversation_memory import ConversationMemory
from openhands.utils.prompt import PromptManager


def print_message_structure(messages: list[Message]) -> None:
    """Print the structure of messages in a readable format."""
    print("=" * 80)
    print("MESSAGES STRUCTURE")
    print("=" * 80)
    
    for i, msg in enumerate(messages):
        print(f"\n--- Message {i+1} ---")
        print(f"Role: {msg.role}")
        print(f"Content items: {len(msg.content)}")
        
        for j, content in enumerate(msg.content):
            if isinstance(content, TextContent):
                print(f"  Content {j+1} (Text): {content.text[:100]}{'...' if len(content.text) > 100 else ''}")
            elif isinstance(content, ImageContent):
                print(f"  Content {j+1} (Image): {len(content.image_urls)} image(s)")
        
        if msg.tool_calls:
            print(f"Tool calls: {len(msg.tool_calls)}")
            for k, tool_call in enumerate(msg.tool_calls):
                print(f"  Tool call {k+1}: {tool_call.function.name}")
        
        if msg.tool_call_id:
            print(f"Tool call ID: {msg.tool_call_id}")
            print(f"Tool name: {msg.name}")
        
        print(f"Serialized: {json.dumps(msg.model_dump(), indent=2)}")


def create_demo_conversation():
    """Create a demo conversation to show message structure."""
    
    # Create basic config and prompt manager
    config = AgentConfig()
    prompt_dir = "/workspace/OpenHands/openhands/agenthub/codeact_agent/prompts"
    prompt_manager = PromptManager(prompt_dir)
    
    # Create conversation memory
    conv_memory = ConversationMemory(config, prompt_manager)
    
    # Create some sample events
    from openhands.events.event import EventSource
    
    # System message
    system_msg = SystemMessageAction(content="You are OpenHands, an AI assistant that can help with software development tasks.")
    system_msg._source = EventSource.AGENT
    
    # Initial user message
    user_msg1 = MessageAction(content="Hello! Can you help me create a simple Python script?")
    user_msg1._source = EventSource.USER
    
    # Agent response
    agent_msg1 = MessageAction(content="I'd be happy to help you create a Python script! What would you like the script to do?")
    agent_msg1._source = EventSource.AGENT
    
    # User follow-up
    user_msg2 = MessageAction(content="I want a script that prints 'Hello World'")
    user_msg2._source = EventSource.USER
    
    # Agent command action
    cmd_action = CmdRunAction(command="echo 'print(\"Hello World\")' > hello.py")
    cmd_action._source = EventSource.AGENT
    
    # Command output observation
    cmd_obs = CmdOutputObservation(
        command="echo 'print(\"Hello World\")' > hello.py",
        command_id=1,
        exit_code=0,
        content=""
    )
    cmd_obs._source = EventSource.ENVIRONMENT
    
    # Agent message about completion
    agent_msg2 = MessageAction(content="I've created a simple Python script called 'hello.py' that prints 'Hello World'. You can run it with `python hello.py`.")
    agent_msg2._source = EventSource.AGENT
    
    events = [
        system_msg,
        user_msg1,
        agent_msg1,
        user_msg2,
        cmd_action,
        cmd_obs,
        agent_msg2,
    ]
    
    # Get initial user action
    initial_user_action = user_msg1
    
    # Process events into messages
    messages = conv_memory.process_events(
        condensed_history=events,
        initial_user_action=initial_user_action,
        max_message_chars=1000,
        vision_is_active=False
    )
    
    return messages


def demonstrate_message_types():
    """Demonstrate different types of messages."""
    print("\n" + "=" * 80)
    print("DIFFERENT MESSAGE TYPES EXAMPLES")
    print("=" * 80)
    
    # 1. System message
    system_msg = Message(
        role='system',
        content=[TextContent(text="You are a helpful AI assistant.")]
    )
    print("\n1. SYSTEM MESSAGE:")
    print(f"   Role: {system_msg.role}")
    print(f"   Content: {system_msg.content[0].text}")
    print(f"   Serialized: {json.dumps(system_msg.model_dump(), indent=2)}")
    
    # 2. User message
    user_msg = Message(
        role='user',
        content=[TextContent(text="What is the weather like today?")]
    )
    print("\n2. USER MESSAGE:")
    print(f"   Role: {user_msg.role}")
    print(f"   Content: {user_msg.content[0].text}")
    print(f"   Serialized: {json.dumps(user_msg.model_dump(), indent=2)}")
    
    # 3. Assistant message
    assistant_msg = Message(
        role='assistant',
        content=[TextContent(text="I don't have access to real-time weather data, but I can help you find weather information.")]
    )
    print("\n3. ASSISTANT MESSAGE:")
    print(f"   Role: {assistant_msg.role}")
    print(f"   Content: {assistant_msg.content[0].text}")
    print(f"   Serialized: {json.dumps(assistant_msg.model_dump(), indent=2)}")
    
    # 4. Message with image (vision)
    vision_msg = Message(
        role='user',
        content=[
            TextContent(text="What do you see in this image?"),
            ImageContent(image_urls=["data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."])
        ],
        vision_enabled=True
    )
    print("\n4. MESSAGE WITH IMAGE:")
    print(f"   Role: {vision_msg.role}")
    print(f"   Text content: {vision_msg.content[0].text}")
    print(f"   Image URLs: {len(vision_msg.content[1].image_urls)} image(s)")
    print(f"   Contains image: {vision_msg.contains_image}")
    print(f"   Serialized: {json.dumps(vision_msg.model_dump(), indent=2)}")
    
    # 5. Tool response message
    tool_msg = Message(
        role='tool',
        content=[TextContent(text="Command executed successfully. Output: Hello World")],
        tool_call_id="call_123",
        name="execute_bash"
    )
    print("\n5. TOOL RESPONSE MESSAGE:")
    print(f"   Role: {tool_msg.role}")
    print(f"   Content: {tool_msg.content[0].text}")
    print(f"   Tool call ID: {tool_msg.tool_call_id}")
    print(f"   Tool name: {tool_msg.name}")
    print(f"   Serialized: {json.dumps(tool_msg.model_dump(), indent=2)}")


if __name__ == "__main__":
    print("OpenHands Message Structure Demo")
    print("This shows what messages look like when sent to the LLM")
    
    # Show different message types
    demonstrate_message_types()
    
    # Show a full conversation
    print("\n" + "=" * 80)
    print("FULL CONVERSATION EXAMPLE")
    print("=" * 80)
    
    try:
        messages = create_demo_conversation()
        print_message_structure(messages)
        
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Total messages in conversation: {len(messages)}")
        print("Message roles:", [msg.role for msg in messages])
        print("Message types:", [type(content).__name__ for msg in messages for content in msg.content])
        
    except Exception as e:
        print(f"Error creating demo conversation: {e}")
        print("This might be due to missing dependencies or configuration.")