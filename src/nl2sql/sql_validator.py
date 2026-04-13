import re
from .base import BaseSQLValidator


class SQLValidator(BaseSQLValidator):
    """SQL验证器"""
    
    def __init__(self):
        """初始化SQL验证器"""
        self.error = None
    
    def validate(self, sql: str) -> bool:
        """验证SQL语句的有效性
        
        Args:
            sql: 要验证的SQL语句
            
        Returns:
            是否有效
        """
        self.error = None
        
        # 检查是否为空
        if not sql or not sql.strip():
            self.error = "SQL语句不能为空"
            return False
        
        # 检查是否包含危险操作
        dangerous_patterns = [
            r'\bDROP\b.*\bTABLE\b',
            r'\bALTER\b.*\bTABLE\b',
            r'\bTRUNCATE\b.*\bTABLE\b',
            r'\bDELETE\b.*\bFROM\b',
            r'\bINSERT\b.*\bINTO\b',
            r'\bUPDATE\b.*\bSET\b',
            r'\bCREATE\b.*\bTABLE\b',
            r'\bGRANT\b',
            r'\bREVOKE\b',
            r'\bEXEC\b',
            r'\bEXECUTE\b',
            r'\bxp_',
            r'\bsp_',
            r'\b;\s*--',
            r'\b;\s*#',
            r'\bUNION\b.*\bSELECT\b',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, sql, re.IGNORECASE):
                self.error = f"SQL语句包含危险操作: {pattern}"
                return False
        
        # 检查SQL语法（简单检查）
        if not re.match(r'^\s*SELECT\s+', sql, re.IGNORECASE):
            # 只允许SELECT语句
            self.error = "只允许SELECT语句"
            return False
        
        # 检查是否包含分号（防止多语句执行）
        if ';' in sql:
            self.error = "SQL语句不应包含分号"
            return False
        
        return True
    
    def get_error(self) -> str:
        """获取验证错误信息
        
        Returns:
            错误信息，如果没有错误则返回None
        """
        return self.error
