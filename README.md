# DB for AI & AI for DB 项目

## 项目概述

这是一个针对华为数据库实习生岗位设计的演示项目，探索**数据库与AI融合**的两个核心方向：
- **AI for DB**：用AI增强数据库功能（如NL2SQL、查询优化）
- **DB for AI**：用数据库支持AI应用（如向量存储、向量检索）

## 核心功能

### 1. AI for DB 功能
- **NL2SQL**：自然语言转SQL查询
- **查询意图理解**：分析查询目的和语义
- **智能查询优化**：利用LLM优化查询计划
- **自然语言交互式数据分析**：端到端的自然语言数据分析

### 2. DB for AI 功能
- **向量存储**：支持FAISS和ChromaDB
- **向量索引构建**：高效的向量索引创建
- **向量检索**：Top-K相似性搜索
- **响应性能**：向量检索响应时间<100ms

## 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.14+ |
| API框架 | FastAPI + Uvicorn |
| 向量数据库 | FAISS, ChromaDB |
| LLM集成 | DeepSeek, OpenAI, HuggingFace |
| 数据库 | SQLAlchemy (SQLite/PostgreSQL/MySQL) |
| 测试 | pytest |

## 安装说明

### 1. 克隆项目
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `.env.example` 文件为 `.env` 并填写相关配置：

```bash
# LLM API 密钥
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# 数据库连接信息
DATABASE_URL=sqlite:///./test.db

# 向量数据库配置
VECTOR_DB_PATH=./vector_db

# API 配置
API_HOST=0.0.0.0
API_PORT=8000

# 日志配置
LOG_LEVEL=INFO
```

## 使用方法

### 1. 启动API服务
```bash
python src/main.py
```

服务将在 `http://localhost:8000` 启动，可访问 `http://localhost:8000/docs` 查看API文档。

### 2. 代码使用示例

#### NL2SQL 使用
```python
from src.nl2sql.service import NL2SQLService

# 使用DeepSeek LLM
service = NL2SQLService(llm_type="deepseek")
result = service.convert(
    "查询所有年龄大于20的用户",
    "CREATE TABLE users (id INT, name TEXT, age INT);"
)
print(result)

# 优化查询
optimize_result = service.optimize_query(
    "SELECT * FROM users WHERE age > 20 ORDER BY name",
    "CREATE TABLE users (id INT, name TEXT, age INT);"
)
print(optimize_result)
```

#### 向量数据库使用
```python
from src.vector_db import VectorIndexBuilder
import numpy as np

# 生成测试向量
vectors = np.random.random((1000, 128)).astype(np.float32)
ids = [f"vec_{i}" for i in range(1000)]
metadata = [{"id": i} for i in range(1000)]

# 使用FAISS构建索引
builder = VectorIndexBuilder(db_type='faiss', dimension=128)
builder.build_index(vectors, ids, metadata)

# 搜索
query_vector = np.random.random(128).astype(np.float32)
result = builder.search(query_vector, k=5)
print(result)

# 添加向量
builder.add_vector(np.random.random(128).astype(np.float32), "vec_1001", {"id": 1001})

# 获取统计信息
stats = builder.get_stats()
print(stats)
```

### 3. API接口使用

#### NL2SQL转换
```bash
curl -X POST http://localhost:8000/nl2sql \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "查询所有年龄大于20的用户",
    "schema": "CREATE TABLE users (id INT, name TEXT, age INT);",
    "llm_type": "deepseek"
  }'
```

#### 执行SQL
```bash
curl -X POST http://localhost:8000/execute-sql \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users WHERE age > 20"
  }'
```

#### 优化查询
```bash
curl -X POST http://localhost:8000/optimize-query \
  -H "Content-Type: application/json" \
  -d '{
    "sql": "SELECT * FROM users WHERE age > 20 ORDER BY name",
    "schema": "CREATE TABLE users (id INT, name TEXT, age INT);",
    "llm_type": "deepseek"
  }'
```

#### 自然语言分析
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "natural_language": "分析年龄大于20的用户数量",
    "schema": "CREATE TABLE users (id INT, name TEXT, age INT);",
    "llm_type": "deepseek",
    "optimize": true
  }'
```

## 项目结构

```
/workspace/
├── src/
│   ├── nl2sql/          # AI for DB 模块
│   │   ├── base.py           # 基础接口定义
│   │   ├── deepseek_llm.py   # DeepSeek LLM集成
│   │   ├── openai_llm.py     # OpenAI LLM集成
│   │   ├── huggingface_llm.py # HuggingFace LLM集成
│   │   ├── mock_llm.py       # 模拟LLM (无API key时使用)
│   │   ├── service.py        # 核心服务
│   │   ├── query_optimizer.py # 查询优化器
│   │   ├── sql_validator.py   # SQL验证器
│   │   └── db_executor.py     # 数据库执行器
│   └── vector_db/        # DB for AI 模块
│       ├── base.py           # 向量数据库基础接口
│       ├── faiss_db.py       # FAISS向量数据库
│       ├── chroma_db.py      # ChromaDB向量数据库
│       ├── factory.py        # 工厂类
│       └── index_builder.py  # 索引构建器
├── api/
│   └── nl2sql_api.py    # RESTful API接口
├── tests/               # 测试文件
├── .env                 # 环境配置
├── requirements.txt     # 依赖包
└── README.md            # 项目文档
```

## 测试

### 运行测试
```bash
python -m pytest tests/
```

### 测试DeepSeek集成
```bash
python test_deepseek.py
```

### 测试向量数据库
```bash
python test_vector_db.py
```

## 核心模块说明

### 1. NL2SQL服务
- **支持多种LLM**：DeepSeek、OpenAI、HuggingFace、Mock
- **智能SQL生成**：根据自然语言和数据库模式生成SQL
- **SQL验证**：确保生成的SQL语法正确且安全
- **错误处理**：提供详细的错误信息

### 2. 查询优化器
- **查询意图分析**：理解查询的目的和语义
- **智能优化建议**：利用LLM生成优化建议
- **效果评估**：比较优化前后的性能和结果

### 3. 向量数据库
- **多引擎支持**：FAISS和ChromaDB
- **高效索引**：支持HNSW等高级索引算法
- **快速检索**：响应时间<100ms
- **灵活配置**：支持不同维度和索引类型

## 性能指标

- **向量检索**：响应时间<100ms（10,000向量）
- **NL2SQL转换**：平均响应时间<1s
- **查询优化**：平均性能提升>30%

## 应用场景

1. **数据分析师**：通过自然语言快速查询数据
2. **开发人员**：快速生成和优化SQL
3. **AI工程师**：构建基于向量的语义搜索
4. **数据库管理员**：智能查询优化和性能调优

## 扩展性

- **新增LLM**：可通过实现 `BaseLLM` 接口添加新的LLM
- **新增向量数据库**：可通过实现 `VectorDB` 接口添加新的向量存储
- **新增API端点**：可在 `nl2sql_api.py` 中添加新的接口

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题，请联系项目维护者。