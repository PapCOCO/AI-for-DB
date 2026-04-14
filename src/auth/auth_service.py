from .user import User, fake_users_db

class AuthService:
    """认证服务"""
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """验证用户"""
        user = fake_users_db.get(username)
        if not user or not user.verify_password(password):
            return None
        return user
    
    @staticmethod
    def create_access_token(user: User) -> str:
        """创建访问令牌"""
        return user.create_access_token(data={"sub": user.username, "role": user.role})
    
    @staticmethod
    def get_user_by_username(username: str) -> User:
        """根据用户名获取用户"""
        return fake_users_db.get(username)
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """验证令牌"""
        return User.verify_token(token)