import os
from typing import Optional
from openai import OpenAI
from .base import BaseLLM


class DeepSeekLLM(BaseLLM):
    """DeepSeek LLM实现"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-chat"):
        """初始化DeepSeek LLM
        
        Args:
            api_key: DeepSeek API密钥，如果为None则从环境变量获取
            model: 使用的模型名称，默认为"deepseek-chat"
        """
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key is required")
        
        # DeepSeek API兼容OpenAI接口格式
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
        self.model = model
    
    def generate_sql(self, natural_language: str, schema: str) -> str:
        """根据自然语言生成SQL
        
        Args:
            natural_language: 自然语言查询
            schema: 数据库模式信息
            
        Returns:
            生成的SQL语句
        """
        prompt = f"""你是一个SQL生成专家。请根据以下数据库模式和自然语言查询生成对应的SQL语句。

数据库模式：
{schema}

自然语言查询：
{natural_language}

要求：
1. 只生成SQL语句，不要包含任何解释或额外文本
2. 确保SQL语句语法正确
3. 使用适当的表名和列名
4. 考虑查询的语义正确性
5. 处理NULL值和边界情况
6. 如果查询是询问"库里面有什么"、"数据库中有什么"、"数据库里有什么"、"查看数据库内容"等类似含义，应该：
   - 对于SQLite：使用 `SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'` 查询所有表
   - 对于MySQL：使用 `SHOW TABLES` 查询所有表
   - 或者使用UNION查询展示所有表的前几行数据样例

SQL语句：
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个SQL生成专家，能够根据数据库模式和自然语言查询生成准确的SQL语句。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个数据分析专家，能够根据查询结果生成清晰、准确的自然语言总结。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # 降低随机性，提高准确性
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
