from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np


class VectorDB(ABC):
    """向量数据库基础接口"""
    
    @abstractmethod
    def add_vector(self, vector: np.ndarray, vector_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加向量
        
        Args:
            vector: 向量数据
            vector_id: 向量ID
            metadata: 向量元数据
            
        Returns:
            是否添加成功
        """
        pass
    
    @abstractmethod
    def add_vectors(self, vectors: List[np.ndarray], vector_ids: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """批量添加向量
        
        Args:
            vectors: 向量列表
            vector_ids: 向量ID列表
            metadatas: 向量元数据列表
            
        Returns:
            是否添加成功
        """
        pass
    
    @abstractmethod
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量
        
        Args:
            query_vector: 查询向量
            k: 返回结果数量
            
        Returns:
            搜索结果列表，每个元素包含向量ID、相似度和元数据
        """
        pass
    
    @abstractmethod
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """获取向量
        
        Args:
            vector_id: 向量ID
            
        Returns:
            向量信息，包含向量数据和元数据
        """
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id: str) -> bool:
        """删除向量
        
        Args:
            vector_id: 向量ID
            
        Returns:
            是否删除成功
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息，包含向量数量、维度等
        """
        pass
