from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class VectorDB(ABC):
    """向量数据库基类"""
    
    @abstractmethod
    def add_vectors(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict[str, Any]] = None) -> None:
        """添加向量"""
        pass
    
    @abstractmethod
    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似向量"""
        pass
    
    @abstractmethod
    def get_vector(self, vector_id: str) -> Tuple[List[float], Dict[str, Any]]:
        """获取向量"""
        pass
    
    @abstractmethod
    def delete_vector(self, vector_id: str) -> None:
        """删除向量"""
        pass
    
    @abstractmethod
    def get_count(self) -> int:
        """获取向量数量"""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """清空向量库"""
        pass
