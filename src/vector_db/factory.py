from typing import Dict, Any, Optional
from .base import VectorDB
from .faiss_db import FAISSDB
from .chroma_db import ChromaDB


class VectorDBFactory:
    """向量数据库工厂类"""
    
    @staticmethod
    def create(db_type: str, **kwargs) -> VectorDB:
        """创建向量数据库实例
        
        Args:
            db_type: 数据库类型，支持"faiss"、"chromadb"
            **kwargs: 初始化参数
            
        Returns:
            VectorDB实例
        """
        if db_type == "faiss":
            return FAISSDB(**kwargs)
        elif db_type == "chromadb":
            return ChromaDB(**kwargs)
        else:
            raise ValueError(f"不支持的向量数据库类型: {db_type}")
