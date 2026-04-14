from fastapi import FastAPI
from .auth import router as auth_router
from .nl2sql import router as nl2sql_router
from .vector import router as vector_router
from .dependencies import setup_mounts

app = FastAPI(title="DB for AI & AI for DB API", description="智能数据库与AI集成平台")

# 设置静态文件挂载
setup_mounts(app)

# 注册路由
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(nl2sql_router, prefix="/api/nl2sql", tags=["nl2sql"])
app.include_router(vector_router, prefix="/api/vector", tags=["vector"])


@app.get("/")
async def root():
    """根路径，返回Web界面"""
    from fastapi.responses import FileResponse
    import os
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
    index_path = os.path.join(web_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DB for AI & AI for DB API Service"}
