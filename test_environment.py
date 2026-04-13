#!/usr/bin/env python3
"""
测试环境配置和依赖安装
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试依赖包导入
try:
    # 数据处理
    import numpy
    import sklearn
    
    # 向量数据库
    import faiss
    import chromadb
    import pymongo
    
    # LLM 接口
    import openai
    import huggingface_hub
    import transformers
    import langchain
    
    # API 框架
    import fastapi
    import uvicorn
    import pydantic
    import pydantic_settings
    
    # 数据库
    import sqlalchemy
    import psycopg2
    import mysql.connector
    
    # 工具
    import loguru
    
    print("✓ 所有依赖包导入成功")
except ImportError as e:
    print(f"✗ 依赖包导入失败: {e}")
    sys.exit(1)

# 测试环境变量配置
print("\n环境变量配置:")
print(f"OPENAI_API_KEY: {'已配置' if os.getenv('OPENAI_API_KEY') else '未配置'}")
print(f"HUGGINGFACE_API_KEY: {'已配置' if os.getenv('HUGGINGFACE_API_KEY') else '未配置'}")
print(f"DATABASE_URL: {'已配置' if os.getenv('DATABASE_URL') else '未配置'}")
print(f"VECTOR_DB_PATH: {'已配置' if os.getenv('VECTOR_DB_PATH') else '未配置'}")
print(f"API_HOST: {'已配置' if os.getenv('API_HOST') else '未配置'}")
print(f"API_PORT: {'已配置' if os.getenv('API_PORT') else '未配置'}")
print(f"LOG_LEVEL: {'已配置' if os.getenv('LOG_LEVEL') else '未配置'}")

# 测试向量数据库连接
try:
    # 测试 FAISS
    import faiss
    index = faiss.IndexFlatL2(128)
    print("\n✓ FAISS 向量数据库初始化成功")
except Exception as e:
    print(f"\n✗ FAISS 向量数据库初始化失败: {e}")

try:
    # 测试 ChromaDB
    import chromadb
    client = chromadb.Client()
    print("✓ ChromaDB 向量数据库初始化成功")
except Exception as e:
    print(f"✗ ChromaDB 向量数据库初始化失败: {e}")

# 测试 API 框架
try:
    from fastapi import FastAPI
    app = FastAPI()
    print("✓ FastAPI 初始化成功")
except Exception as e:
    print(f"✗ FastAPI 初始化失败: {e}")

# 测试 LLM 接口
try:
    from langchain_openai import OpenAI
    print("✓ LangChain OpenAI 接口初始化成功")
except Exception as e:
    print(f"✗ LangChain OpenAI 接口初始化失败: {e}")

print("\n环境测试完成!")
