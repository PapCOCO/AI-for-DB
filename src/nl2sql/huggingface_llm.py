import os
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
from .base import BaseLLM


class HuggingFaceLLM(BaseLLM):
    """HuggingFace LLM实现"""
    
    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.2", api_key: Optional[str] = None):
        """初始化HuggingFace LLM
        
        Args:
            model_name: 模型名称
            api_key: HuggingFace API密钥，如果为None则从环境变量获取
        """
        api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        if not api_key:
            raise ValueError("HuggingFace API key is required")
        
        os.environ["HUGGINGFACE_API_KEY"] = api_key
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.model_name = model_name
    
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
        
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.1,
            top_p=0.95
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # 提取SQL语句部分
        if "SQL语句：" in response:
            sql = response.split("SQL语句：")[1].strip()
        else:
            sql = response.strip()
        
        return sql
    
    def generate_text(self, prompt: str) -> str:
        """生成文本
        
        Args:
            prompt: 提示词
            
        Returns:
            生成的文本
        """
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.1,
            top_p=0.95
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
