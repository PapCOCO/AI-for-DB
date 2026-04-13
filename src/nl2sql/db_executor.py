import os
from typing import List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DBExecutor:
    """数据库执行器"""
    
    def __init__(self, database_url: str = None):
        """初始化数据库执行器
        
        Args:
            database_url: 数据库连接URL，如果为None则从环境变量获取
        """
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./test.db")
        self.engine = create_engine(self.database_url)
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """执行SQL语句
        
        Args:
            sql: 要执行的SQL语句
            
        Returns:
            包含执行结果的字典
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql))
                
                # 获取列名
                columns = result.keys()
                
                # 转换结果为字典列表
                rows = [dict(zip(columns, row)) for row in result]
                
                return {
                    "success": True,
                    "data": rows,
                    "columns": list(columns),
                    "error": None
                }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "data": [],
                "columns": [],
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "data": [],
                "columns": [],
                "error": str(e)
            }
