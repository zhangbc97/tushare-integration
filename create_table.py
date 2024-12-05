from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable

from tushare_integration.models.stock_basic import StockBasic

engine = create_engine('mysql://localhost/default', echo=False)

create_sql = str(CreateTable(StockBasic.__table__, if_not_exists=True).compile(engine))

print(create_sql)
