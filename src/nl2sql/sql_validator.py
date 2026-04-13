import re
from typing import Optional
from .base import BaseSQLValidator


class SQLValidator(BaseSQLValidator):
    """SQL验证器实现"""
    
    def __init__(self):
        """初始化SQL验证器"""
        self._error = None
    
    def validate(self, sql: str) -> bool:
        """验证SQL语句的有效性
        
        Args:
            sql: 要验证的SQL语句
            
        Returns:
            是否有效
        """
        self._error = None
        
        # 检查SQL是否为空
        if not sql or not sql.strip():
            self._error = "SQL语句不能为空"
            return False
        
        # 检查是否包含危险操作
        dangerous_patterns = [
            r'\bDROP\b.*\bTABLE\b',
            r'\bTRUNCATE\b.*\bTABLE\b',
            r'\bDELETE\b.*\bFROM\b',
            r'\bALTER\b.*\bTABLE\b',
            r'\bINSERT\b.*\bINTO\b',
            r'\bUPDATE\b.*\bSET\b',
            r'\bCREATE\b.*\bTABLE\b',
            r'\bDROP\b.*\bDATABASE\b',
            r'\bSHUTDOWN\b',
            r'\bRESTART\b',
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'\bxp_',
            r'\bsp_',
            r'\bSELECT\b.*\bINTO\b.*\bFROM\b'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                self._error = f"SQL语句包含危险操作: {pattern}"
                return False
        
        # 检查基本语法
        if not re.search(r'^\s*SELECT\b', sql, re.IGNORECASE):
            self._error = "只支持SELECT语句"
            return False
        
        # 检查是否有分号
        if ';' not in sql:
            self._error = "SQL语句缺少分号"
            return False
        
        # 检查括号是否匹配
        open_brackets = sql.count('(')
        close_brackets = sql.count(')')
        if open_brackets != close_brackets:
            self._error = "括号不匹配"
            return False
        
        return True
    
    def get_error(self) -> Optional[str]:
        """获取验证错误信息
        
        Returns:
            错误信息，如果没有错误则返回None
        """
        return self._error
