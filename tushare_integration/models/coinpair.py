# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Coinpair(Base):
    """交易所交易对"""

    __tablename__: str = 'coinpair'
    __api_id__: ClassVar[int] = 51
    __api_name__: ClassVar[str] = 'coinpair'
    __api_title__: ClassVar[str] = '交易所交易对'
    __api_info_title__: ClassVar[str] = '交易所交易对'
    __api_path__: ClassVar[List[str]] = ['另类数据', '基础数据', '交易所交易对']
    __api_path_ids__: ClassVar[List[int]] = [41, 3, 51]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['exchange_pair', 'exchange']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'trade_date': {'type': 'str', 'required': False, 'description': '日期'},
        'exchange': {'type': 'str', 'required': True, 'description': '交易所'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '交易所交易对',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    trade_date = Column(
        'trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='日期'
    )
    exchange = Column('exchange', String(), nullable=False, default="", server_default=text("''"), comment='交易所')
    exchange_pair = Column(
        'exchange_pair', String(), nullable=False, default="", server_default=text("''"), comment='交易所原始交易对名称'
    )
    ts_pair = Column(
        'ts_pair', String(), nullable=False, default="", server_default=text("''"), comment='Tushare标准名称'
    )
