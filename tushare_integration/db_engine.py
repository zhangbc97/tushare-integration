from typing import Any, Dict, List, Optional, Type

import pandas as pd
from sqlalchemy import Select, create_engine, text
from sqlalchemy.engine import URL
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
        """插入或更新数据"""
        if 'clickhouse' in self.settings.database.drivername:
            # ClickHouse使用ReplacingMergeTree引擎，直接插入即可
            self.insert(model, data)
            return

        # MySQL和StarRocks使用ON DUPLICATE KEY UPDATE
        table = model.__table__
        primary_key = model.__primary_key__

        # 构建ON DUPLICATE KEY UPDATE子句
        update_columns = [col.name for col in table.columns if col.name not in primary_key]
        update_stmt = ", ".join([f"{col} = VALUES({col})" for col in update_columns])

        # 构建INSERT语句
        columns = [col.name for col in table.columns]
        placeholders = ", ".join([":" + col for col in columns])

        sql = f"""
            INSERT INTO {self.settings.database.db_name}.{table.name} 
            ({", ".join(columns)}) 
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {update_stmt}
        """

        # 将DataFrame转换为字典列表，并确保所有值都是字符串
        records = []
        for _, row in data.iterrows():
            record = {}
            for col in columns:
                val = row[col]
                record[col] = str(val) if pd.notnull(val) else None
            records.append(record)

        # 执行SQL语句
        self.conn.execute(text(sql), records)

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


class DatabaseEngineFactory:
    @staticmethod
    def create(settings: TushareIntegrationSettings) -> DBEngine:
        return DBEngine(settings)
