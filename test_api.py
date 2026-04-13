import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("开始测试 API 功能")
    print("=" * 60)
    
    # 使用用户提供的DeepSeek API密钥
    api_key = "sk-6da5aa450c94425cbf6fd9025119bded"
    
    # 测试1: 生成SQL
    print("\n测试1: 生成SQL")
    print("-" * 40)
    try:
        response = requests.post(
            f"{BASE_URL}/api/nl2sql/generate",
            json={
                "query": "查询所有产品名称和价格",
                "llm_type": "deepseek",
                "api_key": api_key
            }
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success") and result.get("sql"):
            sql = result["sql"]
            print(f"\n生成的SQL: {sql}")
            
            # 测试2: 执行SQL
            print("\n测试2: 执行SQL")
            print("-" * 40)
            response2 = requests.post(
                f"{BASE_URL}/api/nl2sql/execute",
                json={"sql": sql}
            )
            print(f"状态码: {response2.status_code}")
            result2 = response2.json()
            print(f"结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
        else:
            print("\n❌ 生成SQL失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试3: 构建向量索引
    print("\n测试3: 构建向量索引")
    print("-" * 40)
    try:
        response = requests.post(
            f"{BASE_URL}/api/vector/build",
            json={
                "documents": [
                    "笔记本电脑 5999元",
                    "无线鼠标 89元",
                    "机械键盘 299元"
                ],
                "db_type": "faiss"
            }
        )
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        if result.get("success"):
            # 测试4: 搜索向量
            print("\n测试4: 搜索向量")
            print("-" * 40)
            response2 = requests.post(
                f"{BASE_URL}/api/vector/search",
                json={
                    "query": "键盘",
                    "db_type": "faiss"
                }
            )
            print(f"状态码: {response2.status_code}")
            result2 = response2.json()
            print(f"结果: {json.dumps(result2, ensure_ascii=False, indent=2)}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
