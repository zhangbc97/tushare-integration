# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Weekly(Base):
    """周线行情"""

    __tablename__: str = 'weekly'
    __api_id__: ClassVar[int] = 144
    __api_name__: ClassVar[str] = 'weekly'
    __api_title__: ClassVar[str] = '周线行情'
    __api_info_title__: ClassVar[str] = '周线行情'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '行情数据', '周线行情']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 15, 144]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = ['stock_basic', 'trade_cal']
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': 'TS代码'},
        'trade_date': {'type': 'str', 'required': False, 'description': '交易日期'},
        'start_date': {'type': 'str', 'required': False, 'description': '开始日期'},
        'end_date': {'type': 'str', 'required': False, 'description': '结束日期'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '周线行情',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='')
    trade_date = Column(
        'trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment=''
    )
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    pre_close = Column('pre_close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    change = Column('change', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    pct_chg = Column('pct_chg', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='')
