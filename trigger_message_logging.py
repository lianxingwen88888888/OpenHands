#!/usr/bin/env python3
"""
触发OpenHands消息记录的测试脚本
"""

import os
from openhands.core.config.agent_config import AgentConfig
from openhands.memory.conversation_memory import ConversationMemory
from openhands.utils.prompt import PromptManager
from openhands.events.action.message import MessageAction, SystemMessageAction
from openhands.events.event import EventSource

def test_message_logging():
    """测试消息记录功能"""
    
    print("🚀 触发OpenHands消息记录...")
    
    # 创建配置和提示管理器
    config = AgentConfig()
    prompt_dir = "/workspace/OpenHands/openhands/agenthub/codeact_agent/prompts"
    prompt_manager = PromptManager(prompt_dir)
    
    # 创建对话内存
    conv_memory = ConversationMemory(config, prompt_manager)
    
    # 创建一些示例事件
    system_msg = SystemMessageAction(content="You are OpenHands, an AI assistant.")
    system_msg._source = EventSource.AGENT
    
    user_msg = MessageAction(content="Hello! This is a test message to trigger logging.")
    user_msg._source = EventSource.USER
    
    agent_msg = MessageAction(content="Hello! I received your test message. This will be logged.")
    agent_msg._source = EventSource.AGENT
    
    events = [system_msg, user_msg, agent_msg]
    
    # 处理事件为消息 - 这会触发我们的日志记录
    print("📝 处理事件为消息...")
    messages = conv_memory.process_events(
        condensed_history=events,
        initial_user_action=user_msg,
        max_message_chars=1000,
        vision_is_active=False
    )
    
    print(f"✅ 处理完成，生成了 {len(messages)} 条消息")
    
    # 检查日志目录
    log_dir = "/tmp/openhands_logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.startswith('real_messages_')]
        if log_files:
            latest_log = sorted(log_files)[-1]
            log_path = os.path.join(log_dir, latest_log)
            print(f"📄 最新日志文件: {log_path}")
            
            # 显示日志内容
            import json
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            print(f"📊 日志统计:")
            print(f"   时间戳: {log_data['timestamp']}")
            print(f"   消息总数: {log_data['total_messages']}")
            print(f"   角色分布: {log_data['role_distribution']}")
            
            return log_path
        else:
            print("❌ 没有找到日志文件")
    else:
        print("❌ 日志目录不存在")
    
    return None

if __name__ == "__main__":
    print("OpenHands 真实消息记录测试")
    print("=" * 50)
    
    log_file = test_message_logging()
    
    if log_file:
        print(f"\n🎯 成功！真实的OpenHands消息已记录到:")
        print(f"   {log_file}")
        print("\n你可以查看这个文件来看到真实的messages数组结构！")
    else:
        print("\n❌ 消息记录失败，请检查代码修改是否正确")