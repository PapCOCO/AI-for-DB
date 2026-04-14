import requests
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class NL2SQLGenerator:
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY', '')
        self.api_url = 'https://api.deepseek.com/v1/chat/completions'
    
    def generate_sql(self, natural_language, table_structures):
        """生成 SQL 查询"""
        # 构建 prompt
        prompt = f"""你是一个 SQL 生成助手，需要根据用户的自然语言问题生成 SQL 查询语句。

数据库表结构如下：
{self._format_table_structures(table_structures)}

请根据用户的问题生成 SQL 查询语句，只返回 SQL 语句，不要包含其他内容。

用户问题：{natural_language}
SQL 查询："""
        
        # 构建请求体
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            # 解析响应
            data = response.json()
            sql = data['choices'][0]['message']['content'].strip()
            
            # 清理 SQL 语句（去除可能的 markdown 标记）
            if sql.startswith('```sql'):
                sql = sql[7:].strip()
            if sql.endswith('```'):
                sql = sql[:-3].strip()
            
            return sql, None
        except Exception as e:
            return None, str(e)
    
    def validate_sql(self, sql):
        """验证 SQL 语句是否安全"""
        # 禁止执行高危 SQL
        dangerous_commands = ['DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'INSERT', 'UPDATE']
        
        sql_upper = sql.upper()
        for command in dangerous_commands:
            if command in sql_upper:
                return False, f"禁止执行 {command} 操作"
        
        return True, None
    
    def generate_with_retry(self, natural_language, table_structures, max_retries=3):
        """生成 SQL 并在失败时重试"""
        for attempt in range(max_retries):
            sql, error = self.generate_sql(natural_language, table_structures)
            if error:
                print(f"生成 SQL 失败 (尝试 {attempt+1}/{max_retries}): {error}")
                continue
            
            # 验证 SQL
            valid, error = self.validate_sql(sql)
            if not valid:
                print(f"SQL 验证失败: {error}")
                continue
            
            return sql, None
        
        return None, f"尝试 {max_retries} 次后仍无法生成有效的 SQL"
    
    def _format_table_structures(self, table_structures):
        """格式化表结构为字符串"""
        result = []
        for table_name, columns in table_structures.items():
            result.append(f"表名: {table_name}")
            result.append("列: " + ", ".join(columns))
            result.append("")
        return "\n".join(result)