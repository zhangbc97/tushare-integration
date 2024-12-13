import pandas as pd
from sqlalchemy import Select, create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from tushare_integration.settings import TushareIntegrationSettings


class DBEngine:
    def __init__(self, settings: TushareIntegrationSettings) -> None:
        self.settings = settings
        self.engine = self._create_engine()
        self.conn = self.engine.connect()

    def _create_engine(self):
        """创建数据库引擎"""
        url = URL.create(
            self.settings.database.drivername,
            username=self.settings.database.user,
            password=self.settings.database.password,
            host=self.settings.database.host,
            port=self.settings.database.port,
            database=self.settings.database.db_name,
        )
        return create_engine(url)

    def create_table(self, model) -> None:
        """从模型创建表"""
        create_stmt = CreateTable(model.__table__, if_not_exists=True).compile(dialect=self.engine.dialect)
        self.conn.execute(text(str(create_stmt)))

    def session(self) -> Session:
        """创建会话"""
        return Session(self.engine)

    def insert(self, model, data: pd.DataFrame) -> None:
        """插入数据"""
        data.to_sql(
            model.__tablename__,
            self.conn,
            schema=self.settings.database.db_name,
            if_exists='append',
            index=False,
        )

    def upsert(self, model, data: pd.DataFrame) -> None:
        """插入或更新数据

        对于MySQL使用ON DUPLICATE KEY UPDATE进行upsert操作
        对于其他数据库（ClickHouse、StarRocks等）直接使用insert
        """
        if 'mysql' not in self.settings.database.drivername:
            # 非MySQL数据库直接插入
            self.insert(model, data)
            return

        # MySQL使用ON DUPLICATE KEY UPDATE
        table = model.__table__

        # 将DataFrame转换为字典列表，确保键是字符串类型
        records = [{str(k): v for k, v in record.items()} for record in data.to_dict(orient='records')]

        # 使用SQLAlchemy的insert().on_duplicate_key_update()
        stmt = table.insert()

        # 获取所有非主键列作为更新列
        primary_key = model.__primary_key__
        update_columns = {
            str(col.name): stmt.inserted[col.name] for col in table.columns if col.name not in primary_key
        }

        # 构建upsert语句
        upsert_stmt = stmt.on_duplicate_key_update(**update_columns)

        # 执行语句
        self.conn.execute(upsert_stmt, records)

    def query_df(self, stmt: Select | str) -> pd.DataFrame:
        """执行查询并返回DataFrame

        Args:
            stmt: SQLAlchemy Select 对象或 SQL 字符串

        Returns:
            查询结果的DataFrame
        """
        if isinstance(stmt, str):
            return pd.read_sql(text(stmt), self.conn)

        sql = stmt.compile(dialect=self.engine.dialect, compile_kwargs={"literal_binds": True})
        return pd.read_sql(str(sql), self.conn)
