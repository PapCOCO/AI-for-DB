import os
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Union
from .base import VectorDB


class FAISSDB(VectorDB):
    """FAISS向量数据库实现"""
    
    def __init__(self, dimension: int = 16, index_type: str = "FLAT", save_path: str = None):
        """初始化FAISS向量数据库
        
        Args:
            dimension: 向量维度
            index_type: 索引类型，支持"FLAT"、"HNSW"等
            save_path: 索引保存路径
        """
        self.dimension = dimension
        self.index_type = index_type
        self.save_path = save_path
        self.index = self._create_index()
        self.id_to_metadata = {}
    
    def _create_index(self):
        """创建FAISS索引"""
        if self.index_type == "FLAT":
            return faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "HNSW":
            return faiss.IndexHNSWFlat(self.dimension, 16)  # 16是HNSW的M参数
        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}")
    
    def add_vector(self, vector: np.ndarray, vector_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加向量"""
        try:
            # 确保向量是正确的形状
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
            
            # 添加到索引
            self.index.add(vector)
            
            # 保存ID和元数据
            idx = self.index.ntotal - 1
            self.id_to_metadata[idx] = {
                "vector_id": vector_id,
                "metadata": metadata or {}
            }
            
            return True
        except Exception as e:
            print(f"添加向量失败: {e}")
            return False
    
    def add_vectors(self, vectors: List[np.ndarray], vector_ids: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> bool:
        """批量添加向量"""
        try:
            # 确保向量是正确的形状
            vectors_np = np.array(vectors)
            if vectors_np.ndim == 2:
                # 批量添加
                self.index.add(vectors_np)
                
                # 保存ID和元数据
                start_idx = self.index.ntotal - len(vectors)
                for i, (vector_id, metadata) in enumerate(zip(vector_ids, metadatas or [{}] * len(vectors))):
                    idx = start_idx + i
                    self.id_to_metadata[idx] = {
                        "vector_id": vector_id,
                        "metadata": metadata or {}
                    }
            return True
        except Exception as e:
            print(f"批量添加向量失败: {e}")
            return False
    
    def search(self, query: Union[str, np.ndarray], k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量"""
        try:
            # 如果查询是字符串，转换为向量
            if isinstance(query, str):
                # 使用简单的哈希方法，避免SentenceTransformer问题
                import hashlib
                hash_val = hashlib.md5(query.encode()).digest()
                query_vector = np.array([float(b) / 255.0 for b in hash_val])
            else:
                query_vector = query
            
            # 确保查询向量是正确的形状
            if query_vector.ndim == 1:
                query_vector = query_vector.reshape(1, -1)
            
            # 搜索
            distances, indices = self.index.search(query_vector, k)
            
            # 处理结果
            results = []
            for i in range(len(indices[0])):
                idx = indices[0][i]
                if idx < len(self.id_to_metadata):
                    info = self.id_to_metadata.get(idx, {})
                    metadata = info.get("metadata", {})
                    results.append({
                        "vector_id": info.get("vector_id", f"idx_{idx}"),
                        "distance": float(distances[0][i]),
                        "score": 1.0 / (1.0 + float(distances[0][i])),  # 转换为相似度分数
                        "document": metadata.get("document", ""),
                        "metadata": metadata
                    })
            
            return results
        except Exception as e:
            print(f"搜索失败: {e}")
            return []
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """获取向量"""
        try:
            # 查找向量ID对应的索引
            for idx, info in self.id_to_metadata.items():
                if info.get("vector_id") == vector_id:
                    # 从索引中获取向量
                    # 注意：FAISS不支持直接根据索引获取向量，需要额外存储
                    return {
                        "vector_id": vector_id,
                        "metadata": info.get("metadata", {})
                    }
            return None
        except Exception as e:
            print(f"获取向量失败: {e}")
            return None
    
    def delete_vector(self, vector_id: str) -> bool:
        """删除向量"""
        try:
            # 查找向量ID对应的索引
            idx_to_delete = None
            for idx, info in self.id_to_metadata.items():
                if info.get("vector_id") == vector_id:
                    idx_to_delete = idx
                    break
            
            if idx_to_delete is not None:
                # 注意：FAISS不支持直接删除向量，这里只是从元数据中删除
                del self.id_to_metadata[idx_to_delete]
                # 实际使用中可能需要重建索引
                return True
            return False
        except Exception as e:
            print(f"删除向量失败: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "vector_count": self.index.ntotal,
            "dimension": self.dimension,
            "index_type": self.index_type,
            "metadata_count": len(self.id_to_metadata)
        }
