#!/usr/bin/env python3
"""
DB for AI 功能演示脚本
让您亲身体验数据库如何让AI更强大！
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.vector_db.factory import VectorDBFactory
from src.vector_db.index_builder import VectorIndexBuilder

print("=" * 80)
print("🎯 DB for AI 功能演示")
print("=" * 80)
print("\n📚 什么是 DB for AI？")
print("   数据库帮助AI存储、索引、快速检索大量数据，让AI更强大！")
print()

# 1. 准备一些产品数据
print("📦 步骤1：准备产品数据")
print("-" * 80)
products = [
    "笔记本电脑 - 高性能办公笔记本，价格5999元",
    "无线鼠标 - 人体工学设计无线鼠标，价格89元",
    "机械键盘 - 青轴机械键盘，价格299元",
    "耳机 - 降噪蓝牙耳机，价格199元",
    "显示器 - 27英寸高清显示器，价格1299元",
    "平板电脑 - 10英寸平板电脑，价格1999元",
    "智能手表 - 运动健康智能手表，价格799元",
    "充电宝 - 20000毫安充电宝，价格129元",
    "摄像头 - 1080P高清摄像头，价格159元",
    "音箱 - 蓝牙无线音箱，价格249元"
]

for i, product in enumerate(products, 1):
    print(f"  {i}. {product}")
print()

# 2. 构建向量索引
print("🔍 步骤2：用数据库构建向量索引")
print("-" * 80)
print("   把文本转换成向量并存储到数据库中...")

db = VectorDBFactory.create_vector_db(db_type="faiss")
index_builder = VectorIndexBuilder(vector_db=db)
index_builder.build_index(documents=products)

print("   ✅ 向量索引构建完成！")
print(f"   📊 已存储 {len(products)} 条产品数据")
print()

# 3. 演示搜索功能
print("🎯 步骤3：体验向量搜索的强大！")
print("-" * 80)

search_queries = [
    "键盘",
    "电脑",
    "便宜的电子产品",
    "音频设备",
    "办公设备"
]

for query in search_queries:
    print(f"\n🔍 搜索: \"{query}\"")
    print("   " + "-" * 40)
    
    results = db.search(query=query, k=3)
    
    if results:
        for i, result in enumerate(results, 1):
            score = result.get('score', 0) * 100
            doc = result.get('document', '')
            print(f"   {i}. [相似度: {score:.1f}%] {doc}")
    else:
        print("   ❌ 未找到结果")

print()
print("=" * 80)
print("💡 DB for AI 的强大之处体现在：")
print("=" * 80)
print()
print("1️⃣  **语义理解**")
print("    搜索\"键盘\"能找到\"机械键盘\"，而不只是精确匹配")
print()
print("2️⃣  **相似度排序**")
print("    按相似度自动排序，最相关的结果在最前面")
print()
print("3️⃣  **快速检索**")
print("    即使有100万条数据，也能在毫秒级找到结果")
print()
print("4️⃣  **灵活存储**")
print("    可以存储文本、图像、音频等各种类型的向量")
print()
print("5️⃣  **实际应用**")
print("    - 电商：\"猜你喜欢\"推荐系统")
print("    - 搜索引擎：智能语义搜索")
print("    - 问答系统：找到最相关的答案")
print("    - 内容推荐：根据用户喜好推荐内容")
print()
print("=" * 80)
print("🎊 这就是 DB for AI！数据库让AI更智能、更强大！")
print("=" * 80)
