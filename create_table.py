from sqlalchemy import create_engine, select
from sqlalchemy.schema import CreateTable
from sqlalchemy.sql import insert
from sqlalchemy import func

from tushare_integration.models.limit_list_ths import LimitListThs

database = 'default'
engine = create_engine(f'clickhouse://localhost/{database}', echo=False)

# 设置表的schema为数据库名
table = LimitListThs.__table__
table.schema = database

# 生成建表语句
create_sql = str(CreateTable(table, if_not_exists=True).compile(engine))
print("CREATE TABLE 语句:")
print(create_sql)
print("\n")

# 生成INSERT语句模板
insert_stmt = insert(table).compile(
    engine,
    compile_kwargs={"literal_binds": True}
)
print("INSERT 语句模板:")
print(str(insert_stmt))
print("\n")

# 生成SELECT语句模板
select_stmt = select(func.to_date(LimitListThs.trade_date)).compile(
    engine,
    compile_kwargs={"literal_binds": True}
)
print("SELECT 语句模板:")
print(str(select_stmt))
