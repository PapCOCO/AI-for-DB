import os
import numpy as np
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from .base import VectorDB


class ChromaDB(VectorDB):
    """ChromaDB向量数据库实现"""
    
    def __init__(self, collection_name: str = "default", persist_directory: str = None):
        """初始化ChromaDB向量数据库
        
        Args:
            collection_name: 集合名称
            persist_directory: 持久化目录
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        
        # 初始化ChromaDB客户端
        if persist_directory:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
        else:
            self.client = chromadb.Client(
                settings=Settings(
                    anonymized_telemetry=False
                )
            )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(name=collection_name)
    
    def add_vector(self, vector: np.ndarray, vector_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加向量"""
        try:
            # 确保向量是正确的形状
            if vector.ndim == 2:
                vector = vector[0]
            
            # 添加到集合
            self.collection.add(
                ids=[vector_id],
                embeddings=[vector.tolist()],
                metadatas=[metadata] if metadata else None
            )
            
            return True
        except Exception as e:
            print(f"添加向量失败: {e}")
            return False
    
    def add_vectors(self, vectors: List[np.ndarray], vector_ids: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """批量添加向量"""
        try:
            # 确保向量是正确的形状
            vectors_list = []
            for vector in vectors:
                if vector.ndim == 2:
                    vectors_list.append(vector[0].tolist())
                else:
                    vectors_list.append(vector.tolist())
            
            # 添加到集合
            self.collection.add(
                ids=vector_ids,
                embeddings=vectors_list,
                metadatas=metadatas
            )
            
            return True
        except Exception as e:
            print(f"批量添加向量失败: {e}")
            return False
    
    def search(self, query: str or np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        try:
            # 如果查询是字符串，转换为向量
            if isinstance(query, str):
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer('all-MiniLM-L6-v2')
                    query_vector = model.encode([query])[0]
                except ImportError:
                    # 如果没有安装sentence-transformers，使用简单的向量生成
                    import hashlib
                    hash_val = hashlib.md5(query.encode()).digest()
                    query_vector = np.array([float(b) / 255.0 for b in hash_val])
            else:
                query_vector = query
            
            # 确保查询向量是正确的形状
            if query_vector.ndim == 2:
                query_vector = query_vector[0]
            
            # 搜索
            results = self.collection.query(
                query_embeddings=[query_vector.tolist()],
                n_results=k
            )
            
            # 处理结果
            search_results = []
            if results.get("ids") and results.get("distances") and results.get("metadatas"):
                for i in range(len(results["ids"][0])):
                    metadata = results["metadatas"][0][i] if results["metadatas"][0][i] else {}
                    search_results.append({
                        "vector_id": results["ids"][0][i],
                        "distance": float(results["distances"][0][i]),
                        "score": 1.0 / (1.0 + float(results["distances"][0][i])),  # 转换为相似度分数
                        "document": metadata.get("document", ""),
                        "metadata": metadata
                    })
            
            return search_results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """获取向量"""
        try:
            # 从集合中获取向量
            results = self.collection.get(
                ids=[vector_id]
            )
            
            if results.get("ids") and results["ids"]:
                return {
                    "vector_id": vector_id,
                    "metadata": results.get("metadatas", [{}])[0] or {}
                }
            return None
        except Exception as e:
            print(f"获取向量失败: {e}")
            return None
    
    def delete_vector(self, vector_id: str) -> bool:
        """删除向量"""
        try:
            # 从集合中删除向量
            self.collection.delete(
                ids=[vector_id]
            )
            return True
        except Exception as e:
            print(f"删除向量失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        try:
            # 获取集合中的向量数量
            count = self.collection.count()
            return {
                "vector_count": count,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            print(f"获取统计信息失败: {e}")
            return {
                "vector_count": 0,
                "collection_name": self.collection_name,
                "persist_directory": self.persist_directory
            }
