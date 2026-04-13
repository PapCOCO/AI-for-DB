from typing import Dict, Any, Optional
from .base import BaseLLM, BaseSQLValidator
from .openai_llm import OpenAILLM
from .deepseek_llm import DeepSeekLLM
from .huggingface_llm import HuggingFaceLLM
from .mock_llm import MockLLM
from .sql_validator import SQLValidator
from .query_optimizer import QueryOptimizer


class NL2SQLService:
    """自然语言到SQL转换服务"""
    
    def __init__(self, llm_type: str = "mock", **llm_kwargs):
        """初始化NL2SQL服务
        
        Args:
            llm_type: LLM类型，支持"openai"、"deepseek"、"huggingface"或"mock"
            llm_kwargs: LLM初始化参数
        """
        # 初始化LLM
        if llm_type == "openai":
            try:
                self.llm = OpenAILLM(**llm_kwargs)
            except ValueError:
                # 如果没有API key，使用MockLLM
                self.llm = MockLLM()
        elif llm_type == "deepseek":
            try:
                self.llm = DeepSeekLLM(**llm_kwargs)
            except ValueError:
                # 如果没有API key，使用MockLLM
                self.llm = MockLLM()
        elif llm_type == "huggingface":
            try:
                self.llm = HuggingFaceLLM(**llm_kwargs)
            except ValueError:
                # 如果没有API key，使用MockLLM
                self.llm = MockLLM()
        elif llm_type == "mock":
            self.llm = MockLLM()
        else:
            raise ValueError(f"不支持的LLM类型: {llm_type}")
        
        # 初始化SQL验证器
        self.validator = SQLValidator()
        
        # 初始化查询优化器
        self.optimizer = QueryOptimizer(llm_type=llm_type, **llm_kwargs)
    
    def convert(self, natural_language: str, schema: str) -> Dict[str, Any]:
        """将自然语言转换为SQL
        
        Args:
            natural_language: 自然语言查询
            schema: 数据库模式信息
            
        Returns:
            包含转换结果的字典
        """
        try:
            # 生成SQL
            sql = self.llm.generate_sql(natural_language, schema)
            
            # 清理SQL
            sql = self.validator.clean_sql(sql)
            
            # 验证SQL
            is_valid = self.validator.validate(sql)
            error = self.validator.get_error() if not is_valid else None
            
            return {
                "success": is_valid,
                "natural_language": natural_language,
                "sql": sql,
                "error": error
            }
        except Exception as e:
            return {
                "success": False,
                "natural_language": natural_language,
                "sql": None,
                "error": str(e)
            }
    
    def optimize_query(self, sql: str, schema: str) -> Dict[str, Any]:
        """优化查询计划
        
        Args:
            sql: SQL语句
            schema: 数据库模式信息
            
        Returns:
            包含优化结果的字典
        """
        try:
            # 清理SQL
            sql = self.validator.clean_sql(sql)
            
            # 验证SQL
            is_valid = self.validator.validate(sql)
            if not is_valid:
                return {
                    "success": False,
                    "error": self.validator.get_error()
                }
            
            # 优化查询
            result = self.optimizer.optimize_query(sql, schema)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def evaluate_optimization(self, original_sql: str, optimized_sql: str, db_executor) -> Dict[str, Any]:
        """评估优化效果
        
        Args:
            original_sql: 原始SQL语句
            optimized_sql: 优化后的SQL语句
            db_executor: 数据库执行器实例
            
        Returns:
            包含评估结果的字典
        """
        try:
            # 清理SQL
            original_sql = self.validator.clean_sql(original_sql)
            optimized_sql = self.validator.clean_sql(optimized_sql)
            
            # 验证SQL
            if not self.validator.validate(original_sql):
                return {
                    "success": False,
                    "error": f"原始SQL语句无效: {self.validator.get_error()}"
                }
            
            if not self.validator.validate(optimized_sql):
                return {
                    "success": False,
                    "error": f"优化后的SQL语句无效: {self.validator.get_error()}"
                }
            
            # 评估优化效果
            result = self.optimizer.evaluate_optimization(original_sql, optimized_sql, db_executor)
            return result
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
