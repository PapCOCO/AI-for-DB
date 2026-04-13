import pytest
import numpy as np
from src.vector_db import VectorIndexBuilder


def test_faiss_vector_db():
    """测试FAISS向量数据库"""
    # 初始化向量索引构建器（使用FAISS）
    builder = VectorIndexBuilder(db_type='faiss', dimension=128, index_type='HNSW')
    
    # 生成测试向量
    vectors = np.random.random((100, 128)).astype(np.float32)
    ids = [f"vec_{i}" for i in range(100)]
    metadatas = [{"id": i} for i in range(100)]
    
    # 构建索引
    success = builder.build_index(vectors, ids, metadatas)
    assert success is True
    
    # 测试搜索
    query_vector = np.random.random(128).astype(np.float32)
    results = builder.search(query_vector, k=5)
    assert len(results) <= 5
    assert all("vector_id" in result for result in results)
    assert all("distance" in result for result in results)
    
    # 测试添加单个向量
    new_vector = np.random.random(128).astype(np.float32)
    add_success = builder.add_vector(new_vector, "vec_100", {"id": 100})
    assert add_success is True
    
    # 测试获取统计信息
    stats = builder.get_stats()
    assert "vector_count" in stats
    assert stats["vector_count"] > 0
    assert stats["db_type"] == "faiss"


def test_chroma_vector_db():
    """测试ChromaDB向量数据库"""
    # 初始化向量索引构建器（使用ChromaDB）
    builder = VectorIndexBuilder(db_type='chromadb', collection_name='test_collection')
    
    # 生成测试向量
    vectors = np.random.random((50, 128)).astype(np.float32)
    ids = [f"vec_{i}" for i in range(50)]
    metadatas = [{"id": i} for i in range(50)]
    
    # 构建索引
    success = builder.build_index(vectors, ids, metadatas)
    assert success is True
    
    # 测试搜索
    query_vector = np.random.random(128).astype(np.float32)
    results = builder.search(query_vector, k=3)
    assert len(results) <= 3
    assert all("vector_id" in result for result in results)
    assert all("distance" in result for result in results)
    
    # 测试获取统计信息
    stats = builder.get_stats()
    assert "vector_count" in stats
    assert stats["vector_count"] > 0
    assert stats["db_type"] == "chromadb"
