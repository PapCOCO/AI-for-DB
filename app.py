import streamlit as st
import time
from db import DatabaseManager
from nl2sql import NL2SQLGenerator

# 初始化数据库管理器和 SQL 生成器
db_manager = DatabaseManager()
nl2sql_generator = NL2SQLGenerator()

# 设置页面标题
st.title('AI for DB (NL2SQL) 电商数据库查询工具')

# 侧边栏显示数据库表结构
with st.sidebar:
    st.header('数据库表结构')
    table_structures = db_manager.get_table_structure()
    
    if table_structures:
        for table_name, columns in table_structures.items():
            st.subheader(table_name)
            st.code(', '.join(columns))
    else:
        st.error('无法获取数据库表结构')

# 主界面
st.header('自然语言转 SQL 查询')

# 用户输入自然语言问题
user_input = st.text_area('请输入您的问题:', placeholder='例如: 查找所有订单状态为 completed 的客户信息')

# 执行按钮
if st.button('生成并执行 SQL'):
    if not user_input:
        st.error('请输入问题')
    else:
        # 显示加载状态
        with st.spinner('正在生成 SQL...'):
            # 生成 SQL
            start_time = time.time()
            sql, error = nl2sql_generator.generate_with_retry(user_input, table_structures)
            
            if error:
                st.error(f'生成 SQL 失败: {error}')
            else:
                st.success('SQL 生成成功!')
                st.code(sql, language='sql')
                
                # 执行 SQL
                st.subheader('查询结果')
                with st.spinner('正在执行查询...'):
                    results, exec_error = db_manager.execute_query(sql)
                    
                    if exec_error:
                        st.error(f'执行查询失败: {exec_error}')
                    else:
                        # 计算查询耗时
                        end_time = time.time()
                        query_time = end_time - start_time
                        
                        # 显示结果
                        if results:
                            st.dataframe(results)
                            st.info(f'查询耗时: {query_time:.2f} 秒')
                        else:
                            st.info('查询结果为空')

# 示例问题
st.header('示例问题')
st.markdown('''
- 查找所有订单状态为 completed 的客户信息
- 统计每个分类的商品数量
- 计算每个客户的总订单金额
- 查找最近一周的订单
- 统计每个城市的客户数量
''')