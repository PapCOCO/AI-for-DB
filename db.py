import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'CaocaoJunjun73')
        self.database = os.getenv('DB_NAME', 'ecommerce')
        self.connection = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return True
        except Error as e:
            print(f"数据库连接错误: {e}")
            return False
    
    def disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_table_structure(self):
        """获取所有表的结构"""
        if not self.connect():
            return None
        
        table_structures = {}
        cursor = self.connection.cursor()
        
        try:
            # 获取所有表名
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                # 获取表结构
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                
                table_structures[table_name] = []
                for column in columns:
                    col_name = column[0]
                    col_type = column[1]
                    table_structures[table_name].append(f"{col_name} {col_type}")
        
        except Error as e:
            print(f"获取表结构错误: {e}")
            return None
        finally:
            cursor.close()
            self.disconnect()
        
        return table_structures
    
    def execute_query(self, query):
        """执行 SQL 查询"""
        if not self.connect():
            return None, "数据库连接失败"
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            return results, None
        except Error as e:
            return None, str(e)
        finally:
            cursor.close()
            self.disconnect()