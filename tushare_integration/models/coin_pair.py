# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class CoinPair(Base):
    """交易所交易对(新)"""

    __tablename__: str = 'coin_pair'
    __api_id__: ClassVar[int] = 258
    __api_name__: ClassVar[str] = 'coin_pair'
    __api_title__: ClassVar[str] = '交易所交易对(新)'
    __api_info_title__: ClassVar[str] = '交易所交易对(新)'
    __api_path__: ClassVar[List[str]] = ['另类数据', '行情数据', '交易所交易对（新）']
    __api_path_ids__: ClassVar[List[int]] = [41, 52, 258]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['symbol', 'exchange']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'exchange': {'type': 'str', 'required': False, 'description': '交易所'},
        'ts_code': {'type': 'str', 'required': False, 'description': '交易对代码'},
        'status': {'type': 'str', 'required': False, 'description': ''},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '交易所交易对(新)',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    exchange = Column('exchange', String(), nullable=False, default="", server_default=text("''"), comment='交易所')
    symbol = Column('symbol', String(), nullable=False, default="", server_default=text("''"), comment='交易对')
    is_contract = Column(
        'is_contract', String(), nullable=False, default="", server_default=text("''"), comment='是否合约'
    )
    status = Column(
        'status', String(), nullable=False, default="", server_default=text("''"), comment='状态Y可用N不可用'
    )
    base_coin = Column('base_coin', String(), nullable=False, default="", server_default=text("''"), comment='')
    price_coin = Column('price_coin', String(), nullable=False, default="", server_default=text("''"), comment='')
    listing = Column(
        'listing',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='',
    )
    delivery = Column(
        'delivery',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='',
    )
    listing = Column(
        'listing',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='',
    )
    delivery = Column(
        'delivery',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='',
    )
    create_time = Column(
        'create_time',
        DateTime,
        nullable=False,
        default="1970-01-01 00:00:00",
        server_default=text("'1970-01-01 00:00:00'"),
        comment='',
    )
