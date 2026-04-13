import pytest
from src.nl2sql.service import NL2SQLService
from src.nl2sql.db_executor import DBExecutor


def test_nl2sql_service():
    """测试NL2SQL服务"""
    # 初始化服务（使用mock模式）
    service = NL2SQLService(llm_type="mock")
    
    # 测试自然语言转SQL
    natural_language = "查询所有用户"
    schema = "CREATE TABLE users (id INT, name TEXT, age INT);"
    result = service.convert(natural_language, schema)
    
    assert result["success"] is True
    assert "SELECT" in result["sql"]
    assert "users" in result["sql"]
    
    # 测试查询优化
    sql = "SELECT * FROM users WHERE age > 20"
    optimize_result = service.optimize_query(sql, schema)
    
    assert optimize_result["success"] is True
    assert "original_sql" in optimize_result
    assert "optimized_sql" in optimize_result


def test_db_executor():
    """测试数据库执行器"""
    executor = DBExecutor()
    
    # 测试执行SQL
    sql = "SELECT * FROM users"
    result = executor.execute(sql)
    
    assert result["success"] is True
    assert len(result["data"]) > 0
    assert "id" in result["columns"]
    assert "name" in result["columns"]


def test_query_evaluation():
    """测试查询优化评估"""
    service = NL2SQLService(llm_type="mock")
    executor = DBExecutor()
    
    # 测试评估优化效果
    original_sql = "SELECT * FROM users WHERE age > 20"
    optimized_sql = "SELECT * FROM users WHERE age > 20"
    
    result = service.evaluate_optimization(original_sql, optimized_sql, executor)
    
    assert result["success"] is True
    assert "original_time" in result
    assert "optimized_time" in result
    assert "performance_improvement" in result
