import os
import sys
from typing import cast

from sqlalchemy import Table, create_engine, func, select
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import insert

# 将上一级目录添加到import目录
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tushare_models.core.dml import upsert
from tushare_models.limit_list_ths import LimitListThs

database = 'default'
engine = create_engine(f'duckdb://localhost/{database}', echo=False)

# 获取表对象并设置 schema
table = LimitListThs.__table__
table.schema = database

# 生成建表语句
create_sql = str(CreateTable(cast(Table, table), if_not_exists=True).compile(engine))
print("CREATE TABLE 语句:")
print(create_sql)
print("\n")

# 生成INSERT语句模板
insert_stmt = insert(LimitListThs).compile(engine, compile_kwargs={"literal_binds": True})
print("INSERT 语句模板:")
print(str(insert_stmt))
print("\n")

# 生成UPSERT语句模板
upsert_stmt = upsert(LimitListThs).compile(engine, compile_kwargs={"literal_binds": True})
print("UPSERT 语句模板:")
print(str(upsert_stmt))
print("\n")

# 生成SELECT语句模板
select_stmt = select(func.to_date(LimitListThs.trade_date)).compile(engine, compile_kwargs={"literal_binds": True})
print("SELECT 语句模板:")
print(str(select_stmt))
