from typing import Dict, Any
from .base import VectorDB
from .faiss_db import FAISSDB
from .chroma_db import ChromaDB

class VectorDBFactory:
    """向量数据库工厂类"""
    
    @staticmethod
    def create(db_type: str, **kwargs) -> VectorDB:
        """
        创建向量数据库实例
        
        Args:
            db_type: 数据库类型，支持 'faiss' 和 'chromadb'
            **kwargs: 数据库初始化参数
        
        Returns:
            VectorDB: 向量数据库实例
        """
        if db_type == 'faiss':
            dimension = kwargs.get('dimension', 768)
            index_type = kwargs.get('index_type', 'FlatL2')
            return FAISSDB(dimension=dimension, index_type=index_type)
        elif db_type == 'chromadb':
            collection_name = kwargs.get('collection_name', 'default')
            persist_directory = kwargs.get('persist_directory', None)
            return ChromaDB(collection_name=collection_name, persist_directory=persist_directory)
        else:
            raise ValueError(f"不支持的向量数据库类型: {db_type}")
