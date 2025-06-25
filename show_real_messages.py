#!/usr/bin/env python3
"""
显示真实的OpenHands消息记录
"""

import json
import os
from datetime import datetime

def show_all_logged_messages():
    """显示所有记录的消息"""
    
    log_dir = "/tmp/openhands_logs"
    
    if not os.path.exists(log_dir):
        print("❌ 没有找到日志目录")
        return
    
    log_files = [f for f in os.listdir(log_dir) if f.startswith('real_messages_')]
    
    if not log_files:
        print("❌ 没有找到消息日志文件")
        return
    
    print("🔍 找到的OpenHands消息日志文件:")
    print("=" * 80)
    
    for log_file in sorted(log_files):
        log_path = os.path.join(log_dir, log_file)
        
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            print(f"\n📄 文件: {log_file}")
            print(f"   时间: {log_data['timestamp']}")
            print(f"   消息数: {log_data['total_messages']}")
            print(f"   角色: {log_data['message_roles']}")
            print(f"   分布: {log_data['role_distribution']}")
            
            print(f"\n   消息内容:")
            for i, msg in enumerate(log_data['messages'], 1):
                role = msg['role']
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                print(f"   {i}. [{role.upper()}] {content}")
                
                if 'tool_call_id' in msg:
                    print(f"      Tool: {msg.get('name', 'unknown')} (ID: {msg['tool_call_id']})")
            
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ 读取 {log_file} 失败: {e}")

def show_latest_messages_detail():
    """显示最新消息的详细信息"""
    
    log_dir = "/tmp/openhands_logs"
    log_files = [f for f in os.listdir(log_dir) if f.startswith('real_messages_')]
    
    if not log_files:
        return
    
    latest_file = sorted(log_files)[-1]
    log_path = os.path.join(log_dir, latest_file)
    
    print(f"\n🎯 最新消息详情 ({latest_file}):")
    print("=" * 80)
    
    with open(log_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    print(f"完整JSON结构:")
    print(json.dumps(log_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("OpenHands 真实消息查看器")
    print("=" * 80)
    print("这些是真实的OpenHands系统生成的messages数组！")
    
    show_all_logged_messages()
    show_latest_messages_detail()
    
    print("\n" + "=" * 80)
    print("💡 说明:")
    print("- 这些是真实的OpenHands ConversationMemory.process_events() 输出")
    print("- 每个message都有role、content等标准字段")
    print("- _debug_info 是我添加的额外调试信息")
    print("- 这就是发送给LLM的messages数组的真实结构！")
    print("=" * 80)