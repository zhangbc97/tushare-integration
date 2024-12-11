# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class StkAuctionO(Base):
    """股票开盘集合竞价数据"""

    __tablename__: str = 'stk_auction_o'
    __api_id__: ClassVar[int] = 353
    __api_name__: ClassVar[str] = 'stk_auction_o'
    __api_title__: ClassVar[str] = '股票开盘集合竞价数据'
    __api_info_title__: ClassVar[str] = '股票开盘集合竞价数据'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '特色数据', '股票开盘集合竞价数据']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 291, 353]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'},
        'trade_date': {'type': 'str', 'required': False, 'description': '交易日期(YYYYMMDD)'},
        'start_date': {'type': 'str', 'required': False, 'description': '开始日期(YYYYMMDD)'},
        'end_date': {'type': 'str', 'required': False, 'description': '结束日期(YYYYMMDD)'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '股票开盘集合竞价数据',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    trade_date = Column(
        'trade_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='交易日期',
    )
    close = Column(
        'close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价收盘价'
    )
    open = Column(
        'open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价开盘价'
    )
    high = Column(
        'high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价最高价'
    )
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价最低价')
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价成交量')
    amount = Column(
        'amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价成交额'
    )
    vwap = Column('vwap', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘集合竞价均价')
