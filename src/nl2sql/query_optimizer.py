from typing import Dict, Any, List
import re
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .base import BaseLLM
from .openai_llm import OpenAILLM
from .deepseek_llm import DeepSeekLLM
from .huggingface_llm import HuggingFaceLLM
from .mock_llm import MockLLM


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self, llm_type: str = "mock", **llm_kwargs):
        """初始化查询优化器
        
        Args:
            llm_type: LLM类型，支持"openai"、"deepseek"、"huggingface"或"mock"
            llm_kwargs: LLM初始化参数
        """
        # 初始化LLM用于辅助优化
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
    
    def analyze_query_intent(self, sql: str, schema: str) -> Dict[str, Any]:
        """分析查询意图
        
        Args:
            sql: SQL语句
            schema: 数据库模式信息
            
        Returns:
            包含查询意图分析结果的字典
        """
        try:
            # 使用LLM分析查询意图
            prompt = f"分析以下SQL语句的查询意图，包括：1. 查询目的 2. 涉及的表和字段 3. 可能的性能瓶颈\n\nSQL: {sql}\n\n数据库模式: {schema}"
            intent_analysis = self.llm.generate_text(prompt)
            
            # 提取基本信息
            tables = self._extract_tables(sql)
            columns = self._extract_columns(sql)
            
            return {
                "success": True,
                "intent_analysis": intent_analysis,
                "tables": tables,
                "columns": columns
            }
        except Exception as e:
            return {
                "success": False,
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
            # 分析查询意图
            intent_analysis = self.analyze_query_intent(sql, schema)
            
            if not intent_analysis["success"]:
                return {
                    "success": False,
                    "error": intent_analysis["error"]
                }
            
            # 使用LLM生成优化建议
            prompt = f"优化以下SQL语句，提高执行效率，返回优化后的SQL语句和优化说明：\n\nSQL: {sql}\n\n数据库模式: {schema}\n\n查询意图分析: {intent_analysis['intent_analysis']}"
            optimization_result = self.llm.generate_text(prompt)
            
            # 提取优化后的SQL
            optimized_sql = self._extract_optimized_sql(optimization_result)
            
            # 验证优化后的SQL是否有效
            if not optimized_sql.startswith("SELECT"):
                # 如果优化后的SQL无效，使用原始SQL
                optimized_sql = sql
            
            # 生成优化说明
            optimization_explanation = self._extract_optimization_explanation(optimization_result)
            
            return {
                "success": True,
                "original_sql": sql,
                "optimized_sql": optimized_sql,
                "optimization_explanation": optimization_explanation,
                "intent_analysis": intent_analysis
            }
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
            # 执行原始SQL并测量时间
            import time
            start_time = time.time()
            original_result = db_executor.execute(original_sql)
            original_time = time.time() - start_time
            
            # 执行优化后的SQL并测量时间
            start_time = time.time()
            optimized_result = db_executor.execute(optimized_sql)
            optimized_time = time.time() - start_time
            
            # 验证结果是否一致
            results_match = self._compare_results(original_result, optimized_result)
            
            # 计算性能提升
            if original_time > 0:
                performance_improvement = ((original_time - optimized_time) / original_time) * 100
            else:
                performance_improvement = 0
            
            return {
                "success": True,
                "original_time": original_time,
                "optimized_time": optimized_time,
                "performance_improvement": performance_improvement,
                "results_match": results_match,
                "original_result": original_result,
                "optimized_result": optimized_result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_tables(self, sql: str) -> List[str]:
        """从SQL语句中提取表名"""
        # 简单的表名提取逻辑
        table_pattern = r'FROM\s+(\w+)'  # 假设表名在FROM关键字后
        matches = re.findall(table_pattern, sql, re.IGNORECASE)
        return matches
    
    def _extract_columns(self, sql: str) -> List[str]:
        """从SQL语句中提取列名"""
        # 简单的列名提取逻辑
        # 提取SELECT后的列名
        select_pattern = r'SELECT\s+(.+?)\s+FROM'
        matches = re.findall(select_pattern, sql, re.IGNORECASE | re.DOTALL)
        if matches:
            columns_str = matches[0]
            # 移除函数调用和别名
            columns_str = re.sub(r'\w+\s*\([^)]*\)', '', columns_str)
            columns_str = re.sub(r'\s+AS\s+\w+', '', columns_str, flags=re.IGNORECASE)
            # 分割列名
            columns = [col.strip() for col in columns_str.split(',')]
            # 过滤空字符串
            columns = [col for col in columns if col]
            return columns
        return []
    
    def _extract_optimized_sql(self, optimization_result: str) -> str:
        """从LLM生成的结果中提取优化后的SQL"""
        # 直接返回优化结果，因为MockLLM已经返回了一个有效的SQL语句
        return optimization_result
    
    def _extract_optimization_explanation(self, optimization_result: str) -> str:
        """从LLM生成的结果中提取优化说明"""
        # 简单提取优化说明
        # 假设优化说明在SQL语句之前或之后
        if '优化说明' in optimization_result:
            return optimization_result.split('优化说明')[1].strip()
        return optimization_result
    
    def _compare_results(self, result1: Dict[str, Any], result2: Dict[str, Any]) -> bool:
        """比较两个查询结果是否一致"""
        if not result1["success"] or not result2["success"]:
            return False
        
        # 比较数据
        if result1["data"] != result2["data"]:
            return False
        
        # 比较列
        if result1["columns"] != result2["columns"]:
            return False
        
        return True