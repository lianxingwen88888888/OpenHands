#!/usr/bin/env python3
"""
测试LLM交互记录功能
这个脚本会触发真实的LLM调用并记录完整的请求-响应
"""

import os
from openhands.core.config.llm_config import LLMConfig
from openhands.llm.llm import LLM

def test_llm_interaction_logging():
    """测试LLM交互记录"""
    
    print("🚀 测试LLM交互记录...")
    
    # 创建LLM配置 - 使用一个简单的模型
    config = LLMConfig(
        model="gpt-3.5-turbo",  # 你可以改成其他模型
        api_key=os.getenv("OPENAI_API_KEY", "dummy-key"),  # 需要真实的API key
        max_output_tokens=100,
        temperature=0.1
    )
    
    # 创建LLM实例
    llm = LLM(config)
    
    # 准备测试消息
    test_messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant. Keep responses brief."
        },
        {
            "role": "user", 
            "content": "Hello! This is a test message to trigger LLM logging. Please respond briefly."
        }
    ]
    
    print(f"📤 发送消息到LLM ({config.model})...")
    print(f"   消息数量: {len(test_messages)}")
    print(f"   角色: {[msg['role'] for msg in test_messages]}")
    
    try:
        # 调用LLM - 这会触发我们的日志记录
        response = llm.completion(
            messages=test_messages,
            max_tokens=100,
            temperature=0.1
        )
        
        print("✅ LLM调用成功!")
        print(f"📥 响应内容: {response.choices[0].message.content}")
        
        # 检查日志文件
        log_dir = "/tmp/openhands_logs"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
            if log_files:
                latest_log = sorted(log_files)[-1]
                log_path = os.path.join(log_dir, latest_log)
                print(f"📄 LLM交互日志: {log_path}")
                return log_path
            else:
                print("❌ 没有找到LLM交互日志文件")
        else:
            print("❌ 日志目录不存在")
            
    except Exception as e:
        print(f"❌ LLM调用失败: {e}")
        print("💡 提示: 请确保设置了正确的API密钥")
        
        # 即使失败也检查是否有部分日志
        log_dir = "/tmp/openhands_logs"
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
            if log_files:
                latest_log = sorted(log_files)[-1]
                log_path = os.path.join(log_dir, latest_log)
                print(f"📄 部分日志可能存在: {log_path}")
                return log_path
    
    return None

def test_with_mock_llm():
    """使用模拟LLM进行测试（不需要真实API key）"""
    
    print("\n🎭 使用模拟LLM进行测试...")
    
    # 创建一个简单的模拟响应
    from litellm.types.utils import ModelResponse, Choices, Message as LiteLLMMessage
    from litellm import ChatCompletionMessageToolCall
    
    # 创建LLM配置
    config = LLMConfig(
        model="gpt-3.5-turbo",
        api_key="mock-key",
        max_output_tokens=100
    )
    
    llm = LLM(config)
    
    # 模拟消息
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! This is a mock test."}
    ]
    
    print("📝 准备模拟LLM调用...")
    print("💡 这会记录请求部分，但可能在响应时失败（这是正常的）")
    
    try:
        response = llm.completion(messages=test_messages)
        print("✅ 模拟调用成功")
    except Exception as e:
        print(f"⚠️  模拟调用失败（预期的）: {e}")
        print("📝 但请求部分应该已经被记录")
    
    # 检查日志
    log_dir = "/tmp/openhands_logs"
    if os.path.exists(log_dir):
        log_files = [f for f in os.listdir(log_dir) if f.startswith('llm_interaction_')]
        if log_files:
            latest_log = sorted(log_files)[-1]
            log_path = os.path.join(log_dir, latest_log)
            print(f"📄 找到日志文件: {log_path}")
            return log_path
    
    return None

if __name__ == "__main__":
    print("OpenHands LLM交互记录测试")
    print("=" * 60)
    
    # 首先尝试真实的LLM调用
    log_file = test_llm_interaction_logging()
    
    # 如果真实调用失败，尝试模拟调用
    if not log_file:
        log_file = test_with_mock_llm()
    
    if log_file:
        print(f"\n🎯 成功！LLM交互已记录到:")
        print(f"   {log_file}")
        print("\n你可以查看这个文件来看到:")
        print("   - 发送给LLM的完整messages数组")
        print("   - LLM返回的完整response")
        print("   - 请求参数、延迟、token使用等信息")
    else:
        print("\n❌ 没有生成日志文件")
        print("💡 请检查API密钥设置或网络连接")