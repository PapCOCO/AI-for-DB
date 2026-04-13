from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from src.nl2sql.service import NL2SQLService
from src.nl2sql.db_executor import DBExecutor
from src.vector_db.factory import VectorDBFactory
from src.vector_db.index_builder import VectorIndexBuilder

app = FastAPI(title="DB for AI & AI for DB API", description="智能数据库与AI集成平台")

web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(web_dir, "static")), name="static")

nl2sql_service = NL2SQLService(llm_type="mock")
db_executor = DBExecutor()

vector_dbs = {}
index_builders = {}


class GenerateSQLRequest(BaseModel):
    query: str
    llm_type: str = "deepseek"
    api_key: Optional[str] = None


class ExecuteSQLRequest(BaseModel):
    sql: str


class BuildIndexRequest(BaseModel):
    documents: List[str]
    db_type: str = "faiss"


class DatabaseImportRequest(BaseModel):
    db_type: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    user: str
    password: str
    database: str
    table: str
    column: str
    vector_db_type: str = "faiss"


class DatabaseExploreRequest(BaseModel):
    db_type: str = "mysql"
    host: str = "localhost"
    port: int = 3306
    user: str
    password: str
    database: Optional[str] = None


class SearchVectorRequest(BaseModel):
    query: str
    db_type: str = "faiss"


@app.get("/")
async def root():
    """根路径，返回Web界面"""
    index_path = os.path.join(web_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "DB for AI & AI for DB API Service"}


@app.post("/api/nl2sql/generate", response_model=dict)
async def generate_sql(request: GenerateSQLRequest):
    """生成SQL"""
    temp_env = {}
    original_env = {}
    
    try:
        if request.api_key:
            temp_env[f"{request.llm_type.upper()}_API_KEY"] = request.api_key
        
        for key, value in temp_env.items():
            if key in os.environ:
                original_env[key] = os.environ[key]
            os.environ[key] = value
        
        service = NL2SQLService(llm_type=request.llm_type)
        
        schema = """CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            age INTEGER,
            email TEXT,
            created_at TEXT
        )"""
        
        result = service.convert(request.query, schema)
        
        if result["success"]:
            optimization_tips = None
            try:
                optimize_result = service.optimize_query(result["sql"], schema)
                if optimize_result["success"]:
                    optimization_tips = optimize_result.get("suggestions", [])
            except:
                pass
            
            return {
                "success": True,
                "sql": result["sql"],
                "optimization_tips": optimization_tips
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "生成SQL失败")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        for key in temp_env:
            if key in original_env:
                os.environ[key] = original_env[key]
            else:
                if key in os.environ:
                    del os.environ[key]


@app.post("/api/nl2sql/execute", response_model=dict)
async def execute_sql(request: ExecuteSQLRequest):
    """执行SQL"""
    try:
        result = db_executor.execute(request.sql)
        
        if result["success"]:
            formatted_result = []
            if result.get("data") and result.get("columns"):
                for row in result["data"]:
                    formatted_row = {}
                    for i, col in enumerate(result["columns"]):
                        formatted_row[col] = row[i] if i < len(row) else None
                    formatted_result.append(formatted_row)
            
            return {
                "success": True,
                "result": formatted_result
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "执行SQL失败")
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/vector/build", response_model=dict)
async def build_index(request: BuildIndexRequest):
    """构建向量索引"""
    try:
        db = VectorDBFactory.create_vector_db(db_type=request.db_type)
        index_builder = VectorIndexBuilder(vector_db=db)
        
        index_builder.build_index(documents=request.documents)
        
        vector_dbs[request.db_type] = db
        index_builders[request.db_type] = index_builder
        
        return {
            "success": True,
            "message": "索引构建成功"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/vector/search", response_model=dict)
async def search_vector(request: SearchVectorRequest):
    """搜索向量"""
    try:
        if request.db_type not in vector_dbs:
            return {
                "success": False,
                "error": "请先构建索引"
            }
        
        db = vector_dbs[request.db_type]
        results = db.search(query=request.query, top_k=5)
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "document": result.get("document", ""),
                "score": result.get("score", 0.0)
            })
        
        return {
            "success": True,
            "results": formatted_results
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/vector/import-db", response_model=dict)
async def import_from_database(request: DatabaseImportRequest):
    """从数据库导入数据"""
    try:
        # 尝试导入MySQL连接器
        try:
            import mysql.connector
        except ImportError:
            return {
                "success": False,
                "error": "MySQL连接器未安装，请运行: pip install mysql-connector-python"
            }
        
        # 连接数据库
        conn = mysql.connector.connect(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database
        )
        
        cursor = conn.cursor()
        
        # 查询数据
        query = f"SELECT {request.column} FROM {request.table}"
        cursor.execute(query)
        
        documents = []
        for row in cursor.fetchall():
            if row[0]:
                documents.append(str(row[0]))
        
        cursor.close()
        conn.close()
        
        if not documents:
            return {
                "success": False,
                "error": "数据库中没有找到数据"
            }
        
        # 构建向量索引
        db = VectorDBFactory.create_vector_db(db_type=request.vector_db_type)
        index_builder = VectorIndexBuilder(vector_db=db)
        
        index_builder.build_index(documents=documents)
        
        vector_dbs[request.vector_db_type] = db
        
        return {
            "success": True,
            "message": f"成功从数据库导入 {len(documents)} 条记录并构建索引",
            "document_count": len(documents)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/vector/explore-db", response_model=dict)
async def explore_database(request: DatabaseExploreRequest):
    """探索数据库结构"""
    try:
        # 尝试导入MySQL连接器
        try:
            import mysql.connector
        except ImportError:
            return {
                "success": False,
                "error": "MySQL连接器未安装，请运行: pip install mysql-connector-python"
            }
        
        # 连接数据库
        conn = mysql.connector.connect(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database
        )
        
        cursor = conn.cursor()
        
        result = {}
        
        if not request.database:
            # 列出所有数据库
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            result["databases"] = databases
            result["message"] = f"找到 {len(databases)} 个数据库"
        else:
            # 列出数据库中的表
            cursor.execute("SHOW TABLES")
            tables = [row[0] for row in cursor.fetchall()]
            result["tables"] = tables
            result["message"] = f"数据库 {request.database} 中有 {len(tables)} 个表"
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            **result
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/api/vector/explore-table", response_model=dict)
async def explore_table(request: DatabaseImportRequest):
    """探索表结构"""
    try:
        # 尝试导入MySQL连接器
        try:
            import mysql.connector
        except ImportError:
            return {
                "success": False,
                "error": "MySQL连接器未安装，请运行: pip install mysql-connector-python"
            }
        
        # 连接数据库
        conn = mysql.connector.connect(
            host=request.host,
            port=request.port,
            user=request.user,
            password=request.password,
            database=request.database
        )
        
        cursor = conn.cursor()
        
        # 列出表中的列
        cursor.execute(f"DESCRIBE {request.table}")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[0],
                "type": row[1],
                "null": row[2] == "YES",
                "key": row[3],
                "default": row[4],
                "extra": row[5]
            })
        
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "columns": columns,
            "message": f"表 {request.table} 中有 {len(columns)} 个列"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
