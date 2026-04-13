import faiss
import numpy as np
from typing import List, Dict, Any, Tuple
from .base import VectorDB

class FAISSDB(VectorDB):
    """FAISS向量数据库实现"""
    
    def __init__(self, dimension: int, index_type: str = "FlatL2"):
        """
        初始化FAISS向量数据库
        
        Args:
            dimension: 向量维度
            index_type: 索引类型，默认为FlatL2
        """
        self.dimension = dimension
        self.index_type = index_type
        self.index = self._create_index()
        self.id_map = {}
        self.metadata_map = {}
        self.next_id = 0
    
    def _create_index(self):
        """创建FAISS索引"""
        if self.index_type == "FlatL2":
            return faiss.IndexFlatL2(self.dimension)
        elif self.index_type == "IVF":
            nlist = 100
            return faiss.IndexIVFFlat(faiss.IndexFlatL2(self.dimension), self.dimension, nlist)
        elif self.index_type == "HNSW":
            return faiss.IndexHNSWFlat(self.dimension, 32)
        else:
            raise ValueError(f"不支持的索引类型: {self.index_type}")
    
    def add_vectors(self, vectors: List[List[float]], ids: List[str], metadata: List[Dict[str, Any]] = None) -> None:
        """添加向量"""
        if len(vectors) != len(ids):
            raise ValueError("向量数量与ID数量不匹配")
        
        if metadata and len(metadata) != len(ids):
            raise ValueError("元数据数量与ID数量不匹配")
        
        # 转换为numpy数组
        vectors_np = np.array(vectors, dtype=np.float32)
        
        # 添加到索引
        if hasattr(self.index, 'train') and not self.index.is_trained:
            self.index.train(vectors_np)
        
        # 批量添加向量
        start_id = self.next_id
        self.index.add(vectors_np)
        
        # 映射ID
        for i, vector_id in enumerate(ids):
            idx = start_id + i
            self.id_map[idx] = vector_id
            if metadata:
                self.metadata_map[vector_id] = metadata[i]
            else:
                self.metadata_map[vector_id] = {}
        
        self.next_id += len(vectors)
    
    def search(self, query_vector: List[float], k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """搜索相似向量"""
        # 转换为numpy数组
        query_np = np.array([query_vector], dtype=np.float32)
        
        # 搜索
        distances, indices = self.index.search(query_np, k)
        
        # 处理结果
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx in self.id_map:
                vector_id = self.id_map[idx]
                distance = distances[0][i]
                metadata = self.metadata_map.get(vector_id, {})
                results.append((vector_id, distance, metadata))
        
        return results
    
    def get_vector(self, vector_id: str) -> Tuple[List[float], Dict[str, Any]]:
        """获取向量"""
        # FAISS不支持直接按ID获取向量，需要遍历查找
        for idx, vid in self.id_map.items():
            if vid == vector_id:
                # 这里需要注意，FAISS的IndexFlatL2可以直接获取向量
                # 但其他索引类型可能不支持
                if hasattr(self.index, 'reconstruct'):
                    vector = self.index.reconstruct(idx).tolist()
                    metadata = self.metadata_map.get(vector_id, {})
                    return vector, metadata
                else:
                    raise NotImplementedError("该索引类型不支持获取向量")
        
        raise KeyError(f"向量ID不存在: {vector_id}")
    
    def delete_vector(self, vector_id: str) -> None:
        """删除向量"""
        # 查找向量索引
        idx_to_delete = None
        for idx, vid in self.id_map.items():
            if vid == vector_id:
                idx_to_delete = idx
                break
        
        if idx_to_delete is None:
            raise KeyError(f"向量ID不存在: {vector_id}")
        
        # FAISS的IndexFlatL2不支持删除操作
        # 这里需要重建索引
        new_index = self._create_index()
        new_id_map = {}
        new_metadata_map = {}
        new_next_id = 0
        
        for idx, vid in self.id_map.items():
            if idx != idx_to_delete:
                if hasattr(self.index, 'reconstruct'):
                    vector = self.index.reconstruct(idx)
                    new_index.add(np.array([vector]))
                    new_id_map[new_next_id] = vid
                    new_metadata_map[vid] = self.metadata_map.get(vid, {})
                    new_next_id += 1
        
        # 更新索引和映射
        self.index = new_index
        self.id_map = new_id_map
        self.metadata_map = new_metadata_map
        self.next_id = new_next_id
    
    def get_count(self) -> int:
        """获取向量数量"""
        return self.next_id
    
    def clear(self) -> None:
        """清空向量库"""
        self.index = self._create_index()
        self.id_map = {}
        self.metadata_map = {}
        self.next_id = 0
