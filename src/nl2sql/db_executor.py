import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


class DBExecutor:
    """数据库执行器"""
    
    def __init__(self, db_url: str = None):
        """初始化数据库执行器
        
        Args:
            db_url: 数据库连接URL，如果为None则从环境变量获取
        """
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///./test.db")
        self.engine = create_engine(self.db_url)
        self._init_database()
    
    def _init_database(self):
        """初始化数据库（创建测试表）"""
        try:
            with self.engine.connect() as conn:
                # 创建测试表
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    email TEXT
                )
                """))
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price REAL,
                    category TEXT,
                    description TEXT
                )
                """))
                conn.execute(text("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    amount REAL,
                    order_date TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
                """))
                # 插入测试数据
                conn.execute(text("""
                INSERT OR IGNORE INTO users (id, name, age, email) VALUES
                (1, 'Alice', 25, 'alice@example.com'),
                (2, 'Bob', 30, 'bob@example.com'),
                (3, 'Charlie', 35, 'charlie@example.com')
                """))
                conn.execute(text("""
                INSERT OR IGNORE INTO products (id, name, price, category, description) VALUES
                (1, '笔记本电脑', 5999.0, '电子产品', '高性能办公笔记本'),
                (2, '无线鼠标', 89.0, '电子产品', '人体工学设计无线鼠标'),
                (3, '机械键盘', 299.0, '电子产品', '青轴机械键盘'),
                (4, '耳机', 199.0, '电子产品', '降噪蓝牙耳机'),
                (5, '显示器', 1299.0, '电子产品', '27英寸高清显示器')
                """))
                conn.execute(text("""
                INSERT OR IGNORE INTO orders (id, user_id, amount, order_date) VALUES
                (1, 1, 100.0, '2023-01-01'),
                (2, 1, 200.0, '2023-01-02'),
                (3, 2, 150.0, '2023-01-03')
                """))
                conn.commit()
        except SQLAlchemyError as e:
            print(f"初始化数据库时出错: {e}")
    
    def execute(self, sql: str) -> dict:
        """执行SQL语句
        
        Args:
            sql: 要执行的SQL语句
            
        Returns:
            包含执行结果的字典
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql))
                
                # 获取列名
                columns = list(result.keys())
                
                # 获取数据
                data = []
                for row in result:
                    data.append(list(row))
                
                return {
                    "success": True,
                    "data": data,
                    "columns": columns,
                    "message": "SQL执行成功"
                }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "error": str(e),
                "data": [],
                "columns": []
            }
