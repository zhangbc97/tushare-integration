import threading

import pandas as pd
from sqlalchemy import Select, create_engine, insert, text
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from tushare_integration.logger import get_logger
from tushare_integration.models.core.dml import upsert
from tushare_integration.settings import TushareIntegrationSettings

logger = get_logger()


class DBEngine(object):
    def __init__(self, settings: TushareIntegrationSettings) -> None:
        self._db_lock = threading.RLock()  # 新增数据库操作锁
        self.settings = settings
        logger.info("Initializing database engine...")
        self.engine = create_engine(self.settings.database.get_uri())
        self.conn = self.engine.connect()

    def create_table(self, model) -> None:
        """从模型创建表"""
        with self._db_lock:
            create_stmt = CreateTable(model.__table__, if_not_exists=True).compile(dialect=self.engine.dialect)
            self.conn.execute(text(str(create_stmt)))

    def insert(self, model, data: pd.DataFrame) -> None:
        """插入数据"""
        with self._db_lock:
            self.conn.execute(insert(model).values(data.to_dict(orient='records')))

    def upsert(self, model, data: pd.DataFrame) -> None:
        """插入或更新数据"""
        with self._db_lock:
            self.conn.execute(upsert(model).values(data.to_dict(orient='records')))

    def query_df(self, stmt: Select | str) -> pd.DataFrame:
        """执行查询并返回DataFrame

        Args:
            stmt: SQLAlchemy Select 对象或 SQL 字符串

        Returns:
            查询结果的DataFrame
        """
        with self._db_lock:
            if isinstance(stmt, str):
                return pd.read_sql(text(stmt), self.conn)

            sql = stmt.compile(dialect=self.engine.dialect, compile_kwargs={"literal_binds": True})
            logger.debug(f"Executing SQL: {str(sql)}")
            return pd.read_sql(str(sql), self.conn)

    def session(self) -> Session:
        """创建会话"""
        with self._db_lock:
            return Session(self.engine)
