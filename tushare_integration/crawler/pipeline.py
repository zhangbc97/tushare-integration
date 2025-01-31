import datetime
import logging
from abc import ABC, abstractmethod
from typing import ClassVar, List

import pandas as pd
from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, DateTime, Integer, String, Text

from tushare_integration.crawler.abc import BaseSpider
from tushare_integration.db_engine import DBEngine
from tushare_integration.models.core.base import Base
from tushare_integration.settings import TushareIntegrationSettings


class Pipeline(ABC):
    """管道基类"""

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        """初始化管道

        Args:
            settings: 配置对象
            spider: 爬虫实例
        """
        self.settings = settings
        self.spider = spider

    @abstractmethod
    def process_item(self, item: pd.DataFrame) -> pd.DataFrame | None:
        """处理数据项

        Args:
            item: 数据项(DataFrame)

        Returns:
            处理后的数据项,返回None则中断处理
        """
        raise NotImplementedError

    def close(self):
        """关闭管道（可选实现）"""
        pass


class FillNAPipeline(Pipeline):
    """填充空值管道"""

    @staticmethod
    def get_default_by_column(column: Column):
        if column is None:
            raise ValueError("column_type is None")

        type_name = column.type.python_type.__name__
        if type_name == 'str':
            return ""
        elif type_name == 'float':
            return 0.0
        elif type_name == 'int':
            return 0
        elif type_name == 'date':
            return "1970-01-01"
        elif type_name == 'datetime':
            return "1970-01-01 00:00:00"
        elif type_name == 'dict':
            return '{}'
        else:
            raise ValueError(f"Unsupported python_type: {type_name} for column_type: {column}")

    def process_item(self, item: pd.DataFrame) -> pd.DataFrame | None:
        if item is None or len(item) == 0:
            return None

        model = self.spider.__model__
        for column in model.__table__.columns:
            default = column.default.arg if column.default else self.get_default_by_column(column)  # type: ignore
            with pd.option_context('future.no_silent_downcasting', True):
                item[column.name] = item[column.name].replace({pd.NaT: None}).fillna(default)

        return item


class TransformDTypePipeline(Pipeline):
    """数据类型转换管道"""

    def process_item(self, item: pd.DataFrame) -> pd.DataFrame | None:
        model = self.spider.__model__
        for column in model.__table__.columns:
            python_type = column.type.python_type
            type_name = python_type.__name__
            if type_name == 'str':
                item[column.name] = item[column.name].astype(str)
            elif type_name == 'float':
                item[column.name] = item[column.name].astype(float)
            elif type_name == 'int':
                item[column.name] = item[column.name].astype(int)
            elif type_name == 'date':
                item[column.name] = pd.to_datetime(item[column.name], format='mixed', errors='coerce').dt.date
                item[column.name] = item[column.name].replace({pd.NaT: pd.to_datetime('1971-01-01').date()})
            elif type_name == 'datetime':
                item[column.name] = pd.to_datetime(item[column.name])
            elif type_name == 'dict':
                item[column.name] = item[column.name].apply(lambda x: '{}' if pd.isna(x) else x)
            else:
                raise ValueError(f"Unsupported python_type: {python_type} for column_type: {column.type}")
        return item


class DataPipeline(Pipeline):
    """数据存储管道"""

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self.db_engine = DBEngine(settings)
        self.table_name: str = spider.__model__.__tablename__
        # 在初始化时创建表
        self.db_engine.create_table(spider.__model__)

    def process_item(self, item: pd.DataFrame) -> pd.DataFrame | None:
        if item.empty:
            return item

        model = self.spider.__model__
        if model.__primary_key__:
            item = item.drop_duplicates(subset=model.__primary_key__, keep="last")
            self.db_engine.upsert(model, data=item)
        else:
            logging.debug(f"Insert data into {self.table_name}, data count: {len(item)}")
            self.db_engine.insert(model, data=item)

        return item


class TushareIntegrationLog(Base):
    __tablename__ = 'tushare_integration_log'
    __table_args__ = {'comment': '数据集成日志表'}
    __primary_key__: ClassVar[List[str]] = ['batch_id']

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '数据集成日志表',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    batch_id = Column(String(64), primary_key=True, comment='批次ID')
    spider_name = Column(String(64), nullable=False, comment='爬虫名称')
    description = Column(Text, nullable=False, comment='描述')
    count = Column(Integer, nullable=False, default=0, comment='数量')
    start_time = Column(DateTime, nullable=False, default=datetime.datetime.now, comment='开始时间')
    end_time = Column(DateTime, nullable=False, default=datetime.datetime.now, comment='结束时间')


class RecordLogPipeline(Pipeline):
    """日志记录管道"""

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self.db_engine = DBEngine(settings)
        self.count: int = 0
        self.start_time = datetime.datetime.now()
        self.db_engine.create_table(TushareIntegrationLog)

    def process_item(self, item: pd.DataFrame) -> pd.DataFrame | None:
        self.count += len(item)
        return item

    def close(self):
        """关闭管道时记录日志"""
        log_entry = TushareIntegrationLog(
            batch_id=self.settings.batch_id,
            spider_name=self.spider.__spider_name__,
            description=self.spider.__model__.__api_title__,
            count=self.count,
            start_time=self.start_time,
            end_time=datetime.datetime.now(),
        )
        self.db_engine.insert(
            TushareIntegrationLog,
            pd.DataFrame(
                [
                    {
                        'batch_id': log_entry.batch_id,
                        'spider_name': log_entry.spider_name,
                        'description': log_entry.description,
                        'count': log_entry.count,
                        'start_time': log_entry.start_time,
                        'end_time': log_entry.end_time,
                    }
                ]
            ),
        )
