import os
from typing import Optional
from transformers import pipeline
from .base import BaseLLM


class HuggingFaceLLM(BaseLLM):
    """HuggingFace LLM实现"""
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2"):
        """初始化HuggingFace LLM
        
        Args:
            model_name: 使用的模型名称
        """
        try:
            self.pipe = pipeline("text-generation", model=model_name, device_map="auto")
        except Exception as e:
            raise ValueError(f"Failed to load HuggingFace model: {e}")
    
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

SQL语句：
"""
        
        response = self.pipe(
            prompt,
            max_new_tokens=500,
            temperature=0.1,
            do_sample=False
        )
        
        return response[0]["generated_text"].split("SQL语句：")[-1].strip()
    
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        response = self.pipe(
            prompt,
            max_new_tokens=500,
            temperature=0.1,
            do_sample=False
        )
        
        return response[0]["generated_text"].strip()
