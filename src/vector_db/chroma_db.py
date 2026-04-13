import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Tuple
from .base import VectorDB

class ChromaDB(VectorDB):
    """ChromaDB向量数据库实现"""
    
    def __init__(self, collection_name: str = "default", persist_directory: str = None):
        """
        初始化ChromaDB向量数据库
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化存储目录
        """
        self.collection_name = collection_name
        
        # 配置ChromaDB
        settings = Settings()
        if persist_directory:
            settings.persist_directory = persist_directory
        
        # 创建客户端
        self.client = chromadb.Client(settings)
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_vectors(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict[str, Any]] = None) -> None:
        """添加向量"""
        if len(vectors) != len(ids):
            raise ValueError("向量数量与ID数量不匹配")
        
        # 添加向量到集合
        self.collection.add(
            embeddings=vectors,
            ids=ids,
            metadatas=metadata
        )
    
    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似向量"""
        # 搜索
        results = self.collection.query(
            query_embeddings=[query_vector],
            n_results=k
        )
        
        # 处理结果
        output = []
        if results['ids'] and results['ids'][0]:
            for i, vector_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                output.append((vector_id, distance, metadata))
        
        return output
    
    def get_vector(self, vector_id: str) -> Tuple[List[float], Dict[str, Any]]:
        """获取向量"""
        results = self.collection.get(ids=[vector_id])
        
        if not results['ids']:
            raise KeyError(f"向量ID不存在: {vector_id}")
        
        vector = results['embeddings'][0] if results['embeddings'] else None
        metadata = results['metadatas'][0] if results['metadatas'] else {}
        
        if vector is None:
            raise ValueError(f"无法获取向量: {vector_id}")
        
        return vector, metadata
    
    def delete_vector(self, vector_id: str) -> None:
        """删除向量"""
        self.collection.delete(ids=[vector_id])
    
    def get_count(self) -> int:
        """获取向量数量"""
        # ChromaDB没有直接获取数量的方法，需要通过get来估算
        # 这里使用一个简单的方法，获取所有ID并计算长度
        results = self.collection.get()
        return len(results['ids']) if results['ids'] else 0
    
    def clear(self) -> None:
        """清空向量库"""
        # 删除集合并重新创建
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(name=self.collection_name)
