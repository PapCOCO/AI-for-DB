from .base import BaseLLM


class MockLLM(BaseLLM):
    """模拟LLM实现，用于测试"""
    
    def generate_sql(self, natural_language: str, schema: str) -> str:
        """模拟生成SQL
        
        Args:
            natural_language: 自然语言查询
            schema: 数据库模式信息
            
        Returns:
            生成的SQL语句
        """
        # 简单的模拟实现
        if "查询" in natural_language or "select" in natural_language.lower():
            if "用户" in natural_language or "users" in schema.lower():
                return "SELECT * FROM users"
            elif "订单" in natural_language or "orders" in schema.lower():
                return "SELECT * FROM orders"
            else:
                return "SELECT * FROM table"
        elif "插入" in natural_language or "insert" in natural_language.lower():
            return "INSERT INTO table (column1, column2) VALUES (value1, value2)"
        elif "更新" in natural_language or "update" in natural_language.lower():
            return "UPDATE table SET column1 = value1 WHERE id = 1"
        elif "删除" in natural_language or "delete" in natural_language.lower():
            return "DELETE FROM table WHERE id = 1"
        else:
            return "SELECT * FROM table"
    
    def generate_text(self, prompt: str) -> str:
        """模拟生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        return "这是一个模拟的文本生成结果。在实际使用中，这里会返回LLM生成的真实内容。"
