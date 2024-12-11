# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class CoinBar(Base):
    """数字货币k线行情"""

    __tablename__: str = 'coin_bar'
    __api_id__: ClassVar[int] = 238
    __api_name__: ClassVar[str] = 'coin_bar'
    __api_title__: ClassVar[str] = '数字货币k线行情'
    __api_info_title__: ClassVar[str] = '数字货币分钟'
    __api_path__: ClassVar[List[str]] = ['另类数据', '行情数据', '数字货币k线行情']
    __api_path_ids__: ClassVar[List[int]] = [41, 52, 238]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': '代码'}, 'symbol': {'type': 'str', 'required': False, 'description': '交易所原始代码'}, 'exchange': {'type': 'str', 'required': False, 'description': '交易所'}, 'freq': {'type': 'str', 'required': False, 'description': '频度'}, 'start_date': {'type': 'datetime', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'datetime', 'required': False, 'description': '结束日期'}, 'is_contract': {'type': 'str', 'required': False, 'description': ''}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '数字货币k线行情',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    exchange = Column('exchange', String(), nullable=False, default="", server_default=text("''"), comment='交易所')
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='TS代码')
    symbol = Column('symbol', String(), nullable=False, default="", server_default=text("''"), comment='交易所原始代码')
    freq = Column('freq', String(), nullable=False, default="", server_default=text("''"), comment='频度')
    trade_time = Column('trade_time', String(), nullable=False, default="", server_default=text("''"), comment='交易时间')
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘价')
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='收盘价')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最高价')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最低价')
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交量')
    is_contract = Column('is_contract', String(), nullable=False, default="", server_default=text("''"), comment='是否合约')