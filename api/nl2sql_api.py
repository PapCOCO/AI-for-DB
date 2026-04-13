from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.nl2sql.service import NL2SQLService
from src.nl2sql.db_executor import DBExecutor

app = FastAPI(title="NL2SQL API", description="自然语言到SQL转换服务")

# 初始化服务
nl2sql_service = NL2SQLService(llm_type="mock")
db_executor = DBExecutor()


class NL2SQLRequest(BaseModel):
    """NL2SQL请求模型"""
    natural_language: str
    schema: str
    llm_type: Optional[str] = "openai"


class ExecuteSQLRequest(BaseModel):
    """执行SQL请求模型"""
    sql: str


class OptimizeQueryRequest(BaseModel):
    """查询优化请求模型"""
    sql: str
    schema: str
    llm_type: Optional[str] = "openai"


class EvaluateOptimizationRequest(BaseModel):
    """评估优化效果请求模型"""
    original_sql: str
    optimized_sql: str


class NaturalLanguageAnalysisRequest(BaseModel):
    """自然语言分析请求模型"""
    natural_language: str
    schema: str
    llm_type: Optional[str] = "openai"
    optimize: Optional[bool] = True


@app.post("/nl2sql", response_model=dict)
async def convert_nl2sql(request: NL2SQLRequest):
    """将自然语言转换为SQL"""
    try:
        # 重新初始化服务以支持不同的LLM类型
        service = NL2SQLService(llm_type=request.llm_type)
        result = service.convert(request.natural_language, request.schema)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-sql", response_model=dict)
async def execute_sql(request: ExecuteSQLRequest):
    """执行SQL语句"""
    try:
        result = db_executor.execute(request.sql)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/optimize-query", response_model=dict)
async def optimize_query(request: OptimizeQueryRequest):
    """优化查询计划"""
    try:
        # 重新初始化服务以支持不同的LLM类型
        service = NL2SQLService(llm_type=request.llm_type)
        result = service.optimize_query(request.sql, request.schema)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate-optimization", response_model=dict)
async def evaluate_optimization(request: EvaluateOptimizationRequest):
    """评估优化效果"""
    try:
        # 重新初始化服务
        service = NL2SQLService()
        result = service.evaluate_optimization(request.original_sql, request.optimized_sql, db_executor)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze", response_model=dict)
async def analyze_natural_language(request: NaturalLanguageAnalysisRequest):
    """分析自然语言问题，执行数据分析，以自然语言形式返回结果"""
    try:
        # 重新初始化服务以支持不同的LLM类型
        service = NL2SQLService(llm_type=request.llm_type)
        
        # 1. 将自然语言转换为SQL
        nl2sql_result = service.convert(request.natural_language, request.schema)
        if not nl2sql_result["success"]:
            return {
                "success": False,
                "error": f"NL2SQL转换失败: {nl2sql_result['error']}"
            }
        
        sql = nl2sql_result["sql"]
        
        # 2. 优化SQL（如果需要）
        if request.optimize:
            optimize_result = service.optimize_query(sql, request.schema)
            if optimize_result["success"]:
                optimized_sql = optimize_result["optimized_sql"]
                is_valid = service.validator.validate(optimized_sql)
                # 验证优化后的SQL是否有效
                if is_valid and optimized_sql.startswith("SELECT"):
                    sql = optimized_sql
        
        # 3. 执行SQL获取数据
        execute_result = db_executor.execute(sql)
        if not execute_result["success"]:
            return {
                "success": False,
                "error": f"SQL执行失败: {execute_result['error']}"
            }
        
        # 4. 使用LLM将结果转换为自然语言
        data = execute_result["data"]
        columns = execute_result["columns"]
        
        # 构建提示词
        prompt = f"根据以下查询结果，用自然语言总结分析结果：\n\n"
        prompt += f"原始问题：{request.natural_language}\n\n"
        prompt += f"执行的SQL：{sql}\n\n"
        prompt += f"查询结果：\n"
        
        if data:
            # 构建表格格式
            prompt += " | ".join(columns) + "\n"
            prompt += " | ".join(["---"] * len(columns)) + "\n"
            for row in data:
                row_values = [str(row.get(col, "")) for col in columns]
                prompt += " | ".join(row_values) + "\n"
        else:
            prompt += "无数据\n"
        
        # 生成自然语言总结
        summary = service.llm.generate_text(prompt)
        
        return {
            "success": True,
            "natural_language": request.natural_language,
            "sql": sql,
            "data": data,
            "columns": columns,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """根路径"""
    return {"message": "NL2SQL API Service"}
