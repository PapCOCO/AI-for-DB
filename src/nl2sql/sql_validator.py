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
            r';.*;',  # 多个分号表示多语句
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
        
        return True
    
    def clean_sql(self, sql: str) -> str:
        """清理SQL语句
        
        Args:
            sql: 要清理的SQL语句
            
        Returns:
            清理后的SQL语句
        """
        # 移除首尾空白
        sql = sql.strip()
        
        # 只保留第一条SQL语句（按分号分割）
        if ';' in sql:
            statements = sql.split(';')
            # 找到第一条SELECT语句
            for stmt in statements:
                stmt = stmt.strip()
                if stmt and re.match(r'^\s*SELECT\s+', stmt, re.IGNORECASE):
                    sql = stmt
                    break
        
        # 移除末尾的分号
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # 修复常见的SQL语法错误
        # 1. 修复 "ROM" -> "FROM"
        sql = re.sub(r'\bROM\b', 'FROM', sql, flags=re.IGNORECASE)
        
        # 2. 修复缺失的 SELECT 关键字（如果语句以 FROM 开头）
        if re.match(r'^\s*FROM\s+', sql, re.IGNORECASE):
            sql = 'SELECT * ' + sql
        
        # 3. 修复缺失的 SELECT 关键字（如果语句以 WHERE 开头）
        if re.match(r'^\s*WHERE\s+', sql, re.IGNORECASE):
            sql = 'SELECT * FROM table ' + sql
        
        # 4. 确保以 SELECT 开头
        if not re.match(r'^\s*SELECT\s+', sql, re.IGNORECASE):
            # 如果没有 SELECT 但有 FROM，添加 SELECT *
            if re.search(r'\bFROM\s+\w+', sql, re.IGNORECASE):
                sql = 'SELECT * ' + sql
            else:
                # 否则添加默认的 SELECT
                sql = 'SELECT * FROM table WHERE ' + sql
        
        return sql
    
    def get_error(self) -> str:
        """获取验证错误信息
        
        Returns:
            错误信息，如果没有错误则返回None
        """
        return self.error
