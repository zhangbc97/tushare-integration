from datetime import datetime
from typing import ClassVar, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, DateTime, Integer, String, Text

from tushare_integration.models.core.base import Base


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
    start_time = Column(DateTime, nullable=False, default=datetime.now, comment='开始时间')
    end_time = Column(DateTime, nullable=False, default=datetime.now, comment='结束时间')
