import time
import numpy as np
from typing import List, Dict, Any, Tuple
from .base import VectorDB
from .factory import VectorDBFactory

class VectorIndexBuilder:
    """向量索引构建器"""
    
    def __init__(self, db_type: str = 'faiss', **db_kwargs):
        """
        初始化向量索引构建器
        
        Args:
            db_type: 数据库类型，支持 'faiss' 和 'chromadb'
            **db_kwargs: 数据库初始化参数
        """
        self.db = VectorDBFactory.create(db_type, **db_kwargs)
        self.dimension = db_kwargs.get('dimension', 768)
    
    def build_index(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        构建向量索引
        
        Args:
            vectors: 向量列表
            ids: 向量ID列表
            metadata: 向量元数据列表
        
        Returns:
            Dict: 构建结果
        """
        start_time = time.time()
        
        # 验证输入
        if not vectors:
            raise ValueError("向量列表不能为空")
        
        if len(vectors) != len(ids):
            raise ValueError("向量数量与ID数量不匹配")
        
        # 验证向量维度
        vector_dim = len(vectors[0])
        if vector_dim != self.dimension:
            raise ValueError(f"向量维度不匹配，期望 {self.dimension}，实际 {vector_dim}")
        
        # 添加向量
        self.db.add_vectors(vectors, ids, metadata)
        
        # 计算构建时间
        build_time = time.time() - start_time
        
        return {
            'status': 'success',
            'vector_count': len(vectors),
            'build_time': build_time,
            'dimension': self.dimension
        }
    
    def search(self, query_vector: List[float], k: int = 5) -> Dict[str, Any]:
        """
        搜索相似向量
        
        Args:
            query_vector: 查询向量
            k: 返回结果数量
        
        Returns:
            Dict: 搜索结果
        """
        start_time = time.time()
        
        # 验证向量维度
        if len(query_vector) != self.dimension:
            raise ValueError(f"查询向量维度不匹配，期望 {self.dimension}，实际 {len(query_vector)}")
        
        # 搜索
        results = self.db.search(query_vector, k)
        
        # 计算搜索时间
        search_time = time.time() - start_time
        
        # 转换结果格式
        formatted_results = []
        for vector_id, distance, metadata in results:
            formatted_results.append({
                'id': vector_id,
                'distance': distance,
                'metadata': metadata
            })
        
        return {
            'status': 'success',
            'search_time': search_time,
            'results': formatted_results,
            'response_time_ms': search_time * 1000
        }
    
    def add_vector(self, vector: List[float], vector_id: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        添加单个向量
        
        Args:
            vector: 向量
            vector_id: 向量ID
            metadata: 向量元数据
        
        Returns:
            Dict: 添加结果
        """
        # 验证向量维度
        if len(vector) != self.dimension:
            raise ValueError(f"向量维度不匹配，期望 {self.dimension}，实际 {len(vector)}")
        
        self.db.add_vectors([vector], [vector_id], [metadata] if metadata else None)
        
        return {
            'status': 'success',
            'id': vector_id
        }
    
    def get_vector(self, vector_id: str) -> Dict[str, Any]:
        """
        获取向量
        
        Args:
            vector_id: 向量ID
        
        Returns:
            Dict: 向量信息
        """
        vector, metadata = self.db.get_vector(vector_id)
        
        return {
            'status': 'success',
            'id': vector_id,
            'vector': vector,
            'metadata': metadata
        }
    
    def delete_vector(self, vector_id: str) -> Dict[str, Any]:
        """
        删除向量
        
        Args:
            vector_id: 向量ID
        
        Returns:
            Dict: 删除结果
        """
        self.db.delete_vector(vector_id)
        
        return {
            'status': 'success',
            'id': vector_id
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取向量库统计信息
        
        Returns:
            Dict: 统计信息
        """
        count = self.db.get_count()
        
        return {
            'status': 'success',
            'vector_count': count,
            'dimension': self.dimension
        }
    
    def clear(self) -> Dict[str, Any]:
        """
        清空向量库
        
        Returns:
            Dict: 清空结果
        """
        self.db.clear()
        
        return {
            'status': 'success'
        }
