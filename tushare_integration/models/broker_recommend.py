# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class BrokerRecommend(Base):
    """券商月度金股"""

    __tablename__: str = 'broker_recommend'
    __api_id__: ClassVar[int] = 267
    __api_name__: ClassVar[str] = 'broker_recommend'
    __api_title__: ClassVar[str] = '券商月度金股'
    __api_info_title__: ClassVar[str] = '券商每月荐股'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '特色数据', '券商月度金股']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 291, 267]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'month': {'type': 'str', 'required': True, 'description': '月度（YYYYMM）'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '券商月度金股',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    month = Column('month', String(), nullable=False, default="", server_default=text("''"), comment='月度')
    broker = Column('broker', String(), nullable=False, default="", server_default=text("''"), comment='券商')
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='股票简称')