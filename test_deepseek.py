#!/usr/bin/env python3
"""测试DeepSeek LLM集成"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_deepseek_import():
    """测试DeepSeek模块导入"""
    try:
        from src.nl2sql.deepseek_llm import DeepSeekLLM
        print("✓ DeepSeekLLM导入成功")
        return True
    except Exception as e:
        print(f"✗ DeepSeekLLM导入失败: {e}")
        return False

def test_service_support_deepseek():
    """测试NL2SQLService支持DeepSeek"""
    try:
        from src.nl2sql.service import NL2SQLService
        # 使用mock模式测试，不需要API key
        service = NL2SQLService(llm_type="deepseek")
        print("✓ NL2SQLService支持DeepSeek类型")
        return True
    except Exception as e:
        print(f"✗ NL2SQLService DeepSeek支持测试失败: {e}")
        return False

def test_query_optimizer_support_deepseek():
    """测试QueryOptimizer支持DeepSeek"""
    try:
        from src.nl2sql.query_optimizer import QueryOptimizer
        # 使用mock模式测试，不需要API key
        optimizer = QueryOptimizer(llm_type="deepseek")
        print("✓ QueryOptimizer支持DeepSeek类型")
        return True
    except Exception as e:
        print(f"✗ QueryOptimizer DeepSeek支持测试失败: {e}")
        return False

def test_deepseek_with_api_key():
    """测试DeepSeek API key配置"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key and api_key != "your_deepseek_api_key":
        print("✓ DeepSeek API key已配置")
        try:
            from src.nl2sql.deepseek_llm import DeepSeekLLM
            llm = DeepSeekLLM()
            print("✓ DeepSeekLLM初始化成功")
            
            # 测试生成文本
            test_text = llm.generate_text("你好，请回复'测试成功'")
            print(f"✓ DeepSeekLLM文本生成测试成功: {test_text[:50]}...")
            return True
        except Exception as e:
            print(f"✗ DeepSeek API测试失败: {e}")
            print("提示：请检查您的DeepSeek API key是否正确配置")
            return False
    else:
        print("⚠ DeepSeek API key未配置，请在.env文件中设置DEEPSEEK_API_KEY")
        print("提示：可以使用mock模式测试功能，不需要API key")
        return None

def print_usage_example():
    """打印使用示例"""
    print("\n" + "="*60)
    print("使用DeepSeek的示例代码：")
    print("="*60)
    print("""
1. 在代码中使用：
from src.nl2sql.service import NL2SQLService

# 使用DeepSeek
service = NL2SQLService(llm_type="deepseek")
result = service.convert("查询所有用户", "CREATE TABLE users (id INT, name TEXT);")

2. 通过API使用：
POST /nl2sql
{
  "natural_language": "查询所有用户",
  "schema": "CREATE TABLE users (id INT, name TEXT);",
  "llm_type": "deepseek"
}

3. 配置.env文件：
DEEPSEEK_API_KEY=your_actual_deepseek_api_key_here
""")
    print("="*60)

def main():
    """主测试函数"""
    print("开始测试DeepSeek LLM集成...\n")
    
    results = []
    results.append(("模块导入", test_deepseek_import()))
    results.append(("Service支持", test_service_support_deepseek()))
    results.append(("Optimizer支持", test_query_optimizer_support_deepseek()))
    
    print("\n" + "="*60)
    print("测试结果汇总：")
    print("="*60)
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    # 测试API key
    print("\n" + "="*60)
    api_test_result = test_deepseek_with_api_key()
    
    print_usage_example()
    
    # 检查是否所有基础测试通过
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 DeepSeek LLM集成基础功能测试通过！")
        if api_test_result is None:
            print("   请配置API key以使用完整功能。")
        elif api_test_result:
            print("   API连接测试也通过了！")
    else:
        print("\n❌ 部分测试失败，请检查错误信息。")

if __name__ == "__main__":
    main()
