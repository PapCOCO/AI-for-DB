from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLM(ABC):
    """LLM基础接口"""
    
    @abstractmethod
    def generate_sql(self, natural_language: str, schema: str) -> str:
        """根据自然语言生成SQL
        
        Args:
            natural_language: 自然语言查询
            schema: 数据库模式信息
            
        Returns:
            生成的SQL语句
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        pass


class BaseSQLValidator(ABC):
    """SQL验证器基础接口"""
    
    @abstractmethod
    def validate(self, sql: str) -> bool:
        """验证SQL语句的有效性
        
        Args:
            sql: 要验证的SQL语句
            
        Returns:
            是否有效
        """
        pass
    
    @abstractmethod
    def get_error(self) -> Optional[str]:
        """获取验证错误信息
        
        Returns:
            错误信息，如果没有错误则返回None
        """
        pass
