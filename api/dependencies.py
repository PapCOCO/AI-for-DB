from fastapi import FastAPIfrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cachefrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sqlfrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor =from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    deffrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llfrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llm_type}_{api_key or 'default'}"
        if key not in self._cachefrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llm_type}_{api_key or 'default'}"
        if key not in self._cache:
            self._cache[key] = NL2SQLService(llm_type=llmfrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llm_type}_{api_key or 'default'}"
        if key not in self._cache:
            self._cache[key] = NL2SQLService(llm_type=llm_type, api_key=api_key)
        return self._cache[key]

llmfrom fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llm_type}_{api_key or 'default'}"
        if key not in self._cache:
            self._cache[key] = NL2SQLService(llm_type=llm_type, api_key=api_key)
        return self._cache[key]

llm_cache = LLMCache()

# 使用弱引用字典来存储向量数据库实例，from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from functools import lru_cache
import weakref
from src.nl2sql.db_executor import DBExecutor

# 全局数据库执行器
db_executor = DBExecutor()

# LLM实例缓存 - 复用LLM实例，避免重复创建
class LLMCache:
    def __init__(self):
        self._cache = {}
    
    def get_or_create(self, llm_type: str, api_key: str = None):
        from src.nl2sql.service import NL2SQLService
        key = f"{llm_type}_{api_key or 'default'}"
        if key not in self._cache:
            self._cache[key] = NL2SQLService(llm_type=llm_type, api_key=api_key)
        return self._cache[key]

llm_cache = LLMCache()

# 使用弱引用字典来存储向量数据库实例，当不再使用时会自动释放
vector_dbs = weakref.WeakValueDictionary()
index_builders = weakref.WeakValue