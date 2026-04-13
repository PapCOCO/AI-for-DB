from typing import List, Dict, Any, Optional
import numpy as np
from .factory import VectorDBFactory


class VectorIndexBuilder:
    """向量索引构建器"""
    
    def __init__(self, db_type: str = "faiss", vector_db=None, **kwargs):
        """初始化向量索引构建器
        
        Args:
            db_type: 数据库类型，支持"faiss"、"chromadb"
            vector_db: 已创建的向量数据库实例（可选）
            **kwargs: 初始化参数
        """
        self.db_type = db_type
        if vector_db:
            self.db = vector_db
        else:
            self.db = VectorDBFactory.create(db_type, **kwargs)
    
    def build_index(self, vectors: Optional[List[np.ndarray]] = None, vector_ids: Optional[List[str]] = None, metadatas: Optional[List[Dict[str, Any]]] = None, documents: Optional[List[str]] = None) -> bool:
        """构建向量索引
        
        Args:
            vectors: 向量列表
            vector_ids: 向量ID列表
            metadatas: 向量元数据列表
            documents: 文档列表（如果提供，会自动转换为向量）
            
        Returns:
            是否构建成功
        """
        if documents:
            # 为文档生成向量
            from sentence_transformers import SentenceTransformer
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                vectors = model.encode(documents)
                vector_ids = [f"doc_{i}" for i in range(len(documents))]
                metadatas = [{"document": doc} for doc in documents]
            except ImportError:
                # 如果没有安装sentence-transformers，使用简单的向量生成
                import hashlib
                vectors = []
                vector_ids = []
                metadatas = []
                for i, doc in enumerate(documents):
                    # 使用哈希生成简单的向量
                    hash_val = hashlib.md5(doc.encode()).digest()
                    vector = np.array([float(b) / 255.0 for b in hash_val])
                    vectors.append(vector)
                    vector_ids.append(f"doc_{i}")
                    metadatas.append({"document": doc})
        
        if vectors and vector_ids:
            return self.db.add_vectors(vectors, vector_ids, metadatas)
        return False
    
    def add_vector(self, vector: np.ndarray, vector_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """添加单个向量
        
        Args:
            vector: 向量数据
            vector_id: 向量ID
            metadata: 向量元数据
            
        Returns:
            是否添加成功
        """
        return self.db.add_vector(vector, vector_id, metadata)
    
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """搜索相似向量
        
        Args:
            query_vector: 查询向量
            k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        return self.db.search(query_vector, k)
    
    def get_vector(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """获取向量
        
        Args:
            vector_id: 向量ID
            
        Returns:
            向量信息
        """
        return self.db.get_vector(vector_id)
    
    def delete_vector(self, vector_id: str) -> bool:
        """删除向量
        
        Args:
            vector_id: 向量ID
            
        Returns:
            是否删除成功
        """
        return self.db.delete_vector(vector_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息
        
        Returns:
            统计信息
        """
        stats = self.db.get_stats()
        stats["db_type"] = self.db_type
        return stats
