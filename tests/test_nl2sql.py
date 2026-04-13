import pytest
from src.nl2sql.service import NL2SQLService
from src.nl2sql.db_executor import DBExecutor
from src.nl2sql.sql_validator import SQLValidator


class TestNL2SQL:
    """NL2SQL功能测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.validator = SQLValidator()
        self.db_executor = DBExecutor()
    
    def test_sql_validator(self):
        """测试SQL验证器"""
        # 测试有效的SQL
        valid_sql = "SELECT * FROM users WHERE age > 18;"
        assert self.validator.validate(valid_sql) is True
        assert self.validator.get_error() is None
        
        # 测试无效的SQL（缺少分号）
        invalid_sql = "SELECT * FROM users WHERE age > 18"
        assert self.validator.validate(invalid_sql) is False
        assert self.validator.get_error() == "SQL语句缺少分号"
        
        # 测试危险操作
        dangerous_sql = "DROP TABLE users;"
        assert self.validator.validate(dangerous_sql) is False
        assert "危险操作" in self.validator.get_error()
    
    def test_db_executor(self):
        """测试数据库执行器"""
        # 注意：这里我们不测试CREATE TABLE和INSERT语句，因为SQL验证器只允许SELECT语句
        # 我们直接测试SELECT语句的执行
        select_sql = "SELECT 1 as test;"
        result = self.db_executor.execute(select_sql)
        assert result["success"] is True
        assert len(result["data"]) > 0
        assert result["data"][0]["test"] == 1
    
    @pytest.mark.skip(reason="需要API密钥")
    def test_nl2sql_service(self):
        """测试NL2SQL服务"""
        # 数据库模式
        schema = """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER,
            email TEXT
        );
        """
        
        # 自然语言查询
        natural_language = "查询所有年龄大于20的用户"
        
        # 初始化服务
        service = NL2SQLService(llm_type="openai")
        
        # 转换自然语言到SQL
        result = service.convert(natural_language, schema)
        
        assert result["success"] is True
        assert result["sql"] is not None
        assert "SELECT" in result["sql"]
        assert "age" in result["sql"]
        assert ">" in result["sql"]
        assert "20" in result["sql"]
