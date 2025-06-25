#!/usr/bin/env python3
"""
查看所有记录的LLM交互
显示发送给LLM的messages和LLM的responses
"""

import json
import os
from datetime import datetime

def view_all_llm_interactions():
    """查看所有LLM交互记录"""
    
    log_dir = "/tmp/openhands_logs"
    
    if not os.path.exists(log_dir):
        print("❌ 没有找到日志目录")
        return
    
    # 查找所有类型的日志文件
    message_files = [f for f in os.listdir(log_dir) if f.startswith('real_messages_')]
    llm_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
    
    print("🔍 OpenHands 完整交互记录")
    print("=" * 80)
    
    if message_files:
        print(f"\n📋 ConversationMemory Messages ({len(message_files)} 个文件):")
        print("-" * 50)
        
        for msg_file in sorted(message_files):
            msg_path = os.path.join(log_dir, msg_file)
            try:
                with open(msg_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"📄 {msg_file}")
                print(f"   时间: {data['timestamp']}")
                print(f"   消息数: {data['total_messages']}")
                print(f"   角色分布: {data['role_distribution']}")
                
                # 显示消息摘要
                for i, msg in enumerate(data['messages'][:3], 1):  # 只显示前3条
                    content = msg['content'][:60] + "..." if len(msg['content']) > 60 else msg['content']
                    print(f"   {i}. [{msg['role'].upper()}] {content}")
                
                if len(data['messages']) > 3:
                    print(f"   ... 还有 {len(data['messages']) - 3} 条消息")
                print()
                
            except Exception as e:
                print(f"❌ 读取 {msg_file} 失败: {e}")
    
    if llm_files:
        print(f"\n🤖 LLM交互记录 ({len(llm_files)} 个文件):")
        print("-" * 50)
        
        for llm_file in sorted(llm_files):
            llm_path = os.path.join(log_dir, llm_file)
            try:
                with open(llm_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"📄 {llm_file}")
                print(f"   模型: {data['model']}")
                print(f"   请求时间: {data['timestamp']}")
                print(f"   消息数: {data['total_messages']}")
                print(f"   角色: {data['message_roles']}")
                
                if 'response' in data:
                    resp = data['response']
                    print(f"   响应时间: {resp['response_timestamp']}")
                    print(f"   延迟: {resp['latency_seconds']}秒")
                    
                    content = resp['response_content'][:80] + "..." if len(resp['response_content']) > 80 else resp['response_content']
                    print(f"   响应内容: {content}")
                    
                    if resp['tool_calls']:
                        print(f"   工具调用: {len(resp['tool_calls'])} 个")
                        for tc in resp['tool_calls'][:2]:  # 只显示前2个
                            print(f"     - {tc['function_name']}({tc['function_arguments'][:50]}...)")
                    
                    if 'usage' in resp['raw_response']:
                        usage = resp['raw_response']['usage']
                        print(f"   Token使用: {usage['total_tokens']} (输入:{usage['prompt_tokens']}, 输出:{usage['completion_tokens']})")
                
                print()
                
            except Exception as e:
                print(f"❌ 读取 {llm_file} 失败: {e}")
    
    if not message_files and not llm_files:
        print("❌ 没有找到任何日志文件")
        print("💡 请先运行一些OpenHands操作来生成日志")

def show_latest_interaction_detail():
    """显示最新交互的详细信息"""
    
    log_dir = "/tmp/openhands_logs"
    llm_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
    
    if not llm_files:
        print("❌ 没有找到LLM交互记录")
        return
    
    latest_file = sorted(llm_files)[-1]
    latest_path = os.path.join(log_dir, latest_file)
    
    print(f"\n🎯 最新LLM交互详情 ({latest_file}):")
    print("=" * 80)
    
    with open(latest_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("📤 发送给LLM的Messages:")
    print("-" * 40)
    for i, msg in enumerate(data['messages'], 1):
        print(f"{i}. Role: {msg['role']}")
        print(f"   Content: {msg['content']}")
        if 'tool_call_id' in msg:
            print(f"   Tool Call ID: {msg['tool_call_id']}")
            print(f"   Tool Name: {msg.get('name', 'unknown')}")
        print()
    
    if 'response' in data:
        print("📥 LLM返回的Response:")
        print("-" * 40)
        resp = data['response']
        print(f"Response ID: {resp['response_id']}")
        print(f"Content: {resp['response_content']}")
        print(f"Latency: {resp['latency_seconds']}秒")
        
        if resp['tool_calls']:
            print(f"Tool Calls ({len(resp['tool_calls'])}):")
            for tc in resp['tool_calls']:
                print(f"  - {tc['function_name']}: {tc['function_arguments']}")
        
        print(f"\nRaw Response Structure:")
        print(json.dumps(resp['raw_response'], indent=2, ensure_ascii=False))

def show_summary():
    """显示交互摘要"""
    
    log_dir = "/tmp/openhands_logs"
    
    if not os.path.exists(log_dir):
        return
    
    message_files = [f for f in os.listdir(log_dir) if f.startswith('real_messages_')]
    llm_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
    
    print(f"\n📊 交互摘要:")
    print("=" * 80)
    print(f"ConversationMemory记录: {len(message_files)} 个")
    print(f"LLM交互记录: {len(llm_files)} 个")
    
    if llm_files:
        total_tokens = 0
        total_latency = 0
        models_used = set()
        
        for llm_file in llm_files:
            llm_path = os.path.join(log_dir, llm_file)
            try:
                with open(llm_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                models_used.add(data['model'])
                
                if 'response' in data:
                    resp = data['response']
                    total_latency += resp.get('latency_seconds', 0)
                    
                    if 'usage' in resp['raw_response']:
                        usage = resp['raw_response']['usage']
                        total_tokens += usage.get('total_tokens', 0)
                        
            except:
                continue
        
        print(f"使用的模型: {', '.join(models_used)}")
        print(f"总Token使用: {total_tokens}")
        print(f"平均延迟: {total_latency/len(llm_files):.2f}秒")
    
    print("\n💡 这些日志记录了:")
    print("✅ 每次发送给LLM的完整messages数组")
    print("✅ LLM返回的完整response")
    print("✅ 请求参数、延迟、token使用等元数据")
    print("✅ ConversationMemory处理的事件到消息的转换")

if __name__ == "__main__":
    print("OpenHands LLM交互查看器")
    print("这里显示所有记录的LLM交互数据")
    
    view_all_llm_interactions()
    show_latest_interaction_detail()
    show_summary()
    
    print("\n" + "=" * 80)
    print("🎯 现在你可以看到OpenHands与LLM的完整交互过程！")
    print("包括发送的messages和接收的responses")
    print("=" * 80)