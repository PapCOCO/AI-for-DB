import pytest
from src.nl2sql.service import NL2SQLService
from src.nl2sql.db_executor import DBExecutor
from src.nl2sql.query_optimizer import QueryOptimizer


class TestQueryOptimizer:
    """查询优化器功能测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.db_executor = DBExecutor()
    
    @pytest.mark.skip(reason="需要API密钥")
    def test_analyze_query_intent(self):
        """测试查询意图分析"""
        # 测试SQL
        sql = "SELECT * FROM users WHERE age > 18;"
        # 数据库模式
        schema = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        );
        """
        
        # 初始化优化器
        optimizer = QueryOptimizer(llm_type="openai")
        
        # 分析查询意图
        result = optimizer.analyze_query_intent(sql, schema)
        
        # 验证结果
        assert result["success"] is True
        assert "intent_analysis" in result
        assert "tables" in result
        assert "users" in result["tables"]
        assert "columns" in result
    
    @pytest.mark.skip(reason="需要API密钥")
    def test_optimize_query(self):
        """测试查询优化"""
        # 测试SQL
        sql = "SELECT * FROM users WHERE age > 18;"
        # 数据库模式
        schema = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        );
        """
        
        # 初始化优化器
        optimizer = QueryOptimizer(llm_type="openai")
        
        # 优化查询
        result = optimizer.optimize_query(sql, schema)
        
        # 验证结果
        assert result["success"] is True
        assert "original_sql" in result
        assert "optimized_sql" in result
        assert "optimization_explanation" in result
        assert "intent_analysis" in result
    
    @pytest.mark.skip(reason="需要API密钥")
    def test_evaluate_optimization(self):
        """测试优化效果评估"""
        # 原始SQL
        original_sql = "SELECT 1 as test;"
        # 优化后的SQL（假设）
        optimized_sql = "SELECT 1 as test;"
        
        # 初始化优化器
        optimizer = QueryOptimizer(llm_type="openai")
        
        # 评估优化效果
        result = optimizer.evaluate_optimization(original_sql, optimized_sql, self.db_executor)
        
        # 验证结果
        assert result["success"] is True
        assert "original_time" in result
        assert "optimized_time" in result
        assert "performance_improvement" in result
        assert "results_match" in result