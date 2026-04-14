import hashlib
from datetime import datetime, timedelta
import jwt
import os

# 从环境变量获取JWT密钥，默认值用于开发环境
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User:
    """用户模型"""
    def __init__(self, username: str, password: str, role: str = "user"):
        self.username = username
        self.password_hash = self.hash_password(password)
        self.role = role
        self.created_at = datetime.utcnow()
    
    def hash_password(self, password: str) -> str:
        """加密密码 - 使用简单的SHA256哈希（演示项目用）"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return self.hash_password(password) == self.password_hash
    
    def create_access_token(self, data: dict) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """验证令牌"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

# 模拟用户数据库
fake_users_db = {
    "admin": User("admin", "admin123", "admin"),
    "user": User("user", "user123", "user")
}