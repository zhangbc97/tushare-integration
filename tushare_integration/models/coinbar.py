# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Coinbar(Base):
    """行情接口"""

    __tablename__: str = 'coinbar'
    __api_id__: ClassVar[int] = 4
    __api_name__: ClassVar[str] = 'coinbar'
    __api_title__: ClassVar[str] = '行情接口'
    __api_info_title__: ClassVar[str] = '行情接口'
    __api_path__: ClassVar[List[str]] = ['行情接口']
    __api_path_ids__: ClassVar[List[int]] = []
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'symbol': {'type': 'str', 'required': True, 'description': '数字货币交易对'},
        'start_date': {'type': 'datetime', 'required': False, 'description': '开始时间'},
        'end_date': {'type': 'datetime', 'required': False, 'description': '结束时间'},
        'exchange': {'type': 'str', 'required': True, 'description': '交易所名称'},
        'freq': {'type': 'str', 'required': True, 'description': '行情频率'},
        'contract_type': {'type': 'str', 'required': False, 'description': '合约类型'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '行情接口',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    symbol = Column('symbol', String(), nullable=False, default="", server_default=text("''"), comment='数字货币交易对')
    date = Column(
        'date',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='行情时间',
    )
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘价')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最高价')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最低价')
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='收盘价')
    count = Column(
        'count',
        Integer,
        nullable=False,
        default=0,
        server_default=text("'0'"),
        comment='成交笔数(默认不展示，部分交易所无数据)',
    )
    contract_type = Column(
        'contract_type', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='合约类型'
    )
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交量')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交额')