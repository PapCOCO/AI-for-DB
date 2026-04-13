#!/usr/bin/env python3
"""
测试向量数据库功能
"""

import numpy as np
from src.vector_db import VectorIndexBuilder


def test_faiss_db():
    """测试FAISS向量数据库"""
    print("=== 测试 FAISS 向量数据库 ===")
    
    # 初始化向量索引构建器
    builder = VectorIndexBuilder(db_type='faiss', dimension=128, index_type='FlatL2')
    
    # 生成测试数据
    num_vectors = 1000
    vectors = [np.random.rand(128).tolist() for _ in range(num_vectors)]
    ids = [f'vec_{i}' for i in range(num_vectors)]
    metadata = [{'category': f'cat_{i % 10}'} for i in range(num_vectors)]
    
    # 构建索引
    print("构建索引...")
    build_result = builder.build_index(vectors, ids, metadata)
    print(f"构建结果: {build_result}")
    
    # 测试搜索
    print("\n测试搜索...")
    query_vector = np.random.rand(128).tolist()
    search_result = builder.search(query_vector, k=10)
    print(f"搜索时间: {search_result['response_time_ms']:.2f} ms")
    print(f"搜索结果数量: {len(search_result['results'])}")
    print(f"前3个结果: {search_result['results'][:3]}")
    
    # 测试添加单个向量
    print("\n测试添加单个向量...")
    new_vector = np.random.rand(128).tolist()
    add_result = builder.add_vector(new_vector, 'new_vec', {'category': 'new'})
    print(f"添加结果: {add_result}")
    
    # 测试获取向量
    print("\n测试获取向量...")
    get_result = builder.get_vector('vec_0')
    print(f"获取结果: 向量维度={len(get_result['vector'])}, 元数据={get_result['metadata']}")
    
    # 测试删除向量
    print("\n测试删除向量...")
    delete_result = builder.delete_vector('vec_0')
    print(f"删除结果: {delete_result}")
    
    # 测试统计信息
    print("\n测试统计信息...")
    stats = builder.get_stats()
    print(f"统计信息: {stats}")
    
    # 测试清空
    print("\n测试清空...")
    clear_result = builder.clear()
    print(f"清空结果: {clear_result}")
    
    print("\nFAISS 测试完成！")


def test_chroma_db():
    """测试ChromaDB向量数据库"""
    print("\n=== 测试 ChromaDB 向量数据库 ===")
    
    # 初始化向量索引构建器
    builder = VectorIndexBuilder(db_type='chromadb', collection_name='test_collection')
    
    # 生成测试数据
    num_vectors = 1000
    vectors = [np.random.rand(768).tolist() for _ in range(num_vectors)]
    ids = [f'vec_{i}' for i in range(num_vectors)]
    metadata = [{'category': f'cat_{i % 10}'} for i in range(num_vectors)]
    
    # 构建索引
    print("构建索引...")
    build_result = builder.build_index(vectors, ids, metadata)
    print(f"构建结果: {build_result}")
    
    # 测试搜索
    print("\n测试搜索...")
    query_vector = np.random.rand(768).tolist()
    search_result = builder.search(query_vector, k=10)
    print(f"搜索时间: {search_result['response_time_ms']:.2f} ms")
    print(f"搜索结果数量: {len(search_result['results'])}")
    print(f"前3个结果: {search_result['results'][:3]}")
    
    # 测试添加单个向量
    print("\n测试添加单个向量...")
    new_vector = np.random.rand(768).tolist()
    add_result = builder.add_vector(new_vector, 'new_vec', {'category': 'new'})
    print(f"添加结果: {add_result}")
    
    # 测试获取向量
    # print("\n测试获取向量...")
    # get_result = builder.get_vector('vec_0')
    # print(f"获取结果: 向量维度={len(get_result['vector'])}, 元数据={get_result['metadata']}")
    
    # 测试删除向量
    print("\n测试删除向量...")
    delete_result = builder.delete_vector('vec_0')
    print(f"删除结果: {delete_result}")
    
    # 测试统计信息
    print("\n测试统计信息...")
    stats = builder.get_stats()
    print(f"统计信息: {stats}")
    
    # 测试清空
    print("\n测试清空...")
    clear_result = builder.clear()
    print(f"清空结果: {clear_result}")
    
    print("\nChromaDB 测试完成！")


def test_response_time():
    """测试响应时间"""
    print("\n=== 测试响应时间 ===")
    
    # 初始化FAISS向量数据库
    builder = VectorIndexBuilder(db_type='faiss', dimension=128, index_type='HNSW')
    
    # 生成更多测试数据
    num_vectors = 10000
    vectors = [np.random.rand(128).tolist() for _ in range(num_vectors)]
    ids = [f'vec_{i}' for i in range(num_vectors)]
    
    # 构建索引
    print(f"构建包含 {num_vectors} 个向量的索引...")
    build_result = builder.build_index(vectors, ids)
    print(f"构建时间: {build_result['build_time']:.2f} 秒")
    
    # 测试多次搜索的响应时间
    print("\n测试搜索响应时间...")
    total_time = 0
    num_tests = 100
    
    for i in range(num_tests):
        query_vector = np.random.rand(128).tolist()
        search_result = builder.search(query_vector, k=10)
        total_time += search_result['response_time_ms']
    
    avg_time = total_time / num_tests
    print(f"{num_tests}次搜索平均响应时间: {avg_time:.2f} ms")
    print(f"响应时间是否小于100ms: {avg_time < 100}")
    
    print("\n响应时间测试完成！")


if __name__ == "__main__":
    test_faiss_db()
    test_chroma_db()
    test_response_time()
