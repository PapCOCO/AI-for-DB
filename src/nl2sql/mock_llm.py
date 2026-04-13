from .base import BaseLLM


class MockLLM(BaseLLM):
    """Mock LLM实现，用于测试和演示"""
    
    def generate_sql(self, natural_language: str, schema: str) -> str:
        """根据自然语言生成SQL
        
        Args:
            natural_language: 自然语言查询
            schema: 数据库模式信息
            
        Returns:
            生成的SQL语句
        """
        # 简单的mock实现，返回一个示例SQL语句
        return "SELECT * FROM users LIMIT 10;"
    
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        # 简单的mock实现，根据不同的请求类型返回不同的响应
        if "优化" in prompt:
            # 返回一个优化后的SQL语句
            return "SELECT * FROM users LIMIT 10;"
        elif "分析" in prompt:
            # 返回一个分析结果
            return "查询目的：查询所有用户记录；涉及的表：users；涉及的字段：id, name, email, age；可能的性能瓶颈：无"
        else:
            # 对于其他请求，返回自然语言响应
            return "根据查询结果，我们可以看到有10条用户记录。"
