# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class BakDaily(Base):
    """备用行情"""

    __tablename__: str = 'bak_daily'
    __api_id__: ClassVar[int] = 255
    __api_name__: ClassVar[str] = 'bak_daily'
    __api_title__: ClassVar[str] = '备用行情'
    __api_info_title__: ClassVar[str] = '备用行情'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '行情数据', '备用行情']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 15, 255]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'}, 'trade_date': {'type': 'str', 'required': False, 'description': '交易日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '结束日期'}, 'offset': {'type': 'str', 'required': False, 'description': '开始行数'}, 'limit': {'type': 'str', 'required': False, 'description': '最大行数'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '备用行情',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    trade_date = Column('trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='交易日期')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='股票名称')
    pct_change = Column('pct_change', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='涨跌幅')
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='收盘价')
    change = Column('change', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='涨跌额')
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘价')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最高价')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最低价')
    pre_close = Column('pre_close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='昨收价')
    vol_ratio = Column('vol_ratio', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='量比')
    turn_over = Column('turn_over', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='换手率')
    swing = Column('swing', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='振幅')
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交量')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交额')
    selling = Column('selling', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='内盘')
    buying = Column('buying', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='外盘')
    total_share = Column('total_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='总股本(万)')
    float_share = Column('float_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通股本(万)')
    pe = Column('pe', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='市盈(动)')
    industry = Column('industry', String(), nullable=False, default="", server_default=text("''"), comment='所属行业')
    area = Column('area', String(), nullable=False, default="", server_default=text("''"), comment='所属地域')
    float_mv = Column('float_mv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通市值')
    total_mv = Column('total_mv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='总市值')
    avg_price = Column('avg_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='平均价')
    strength = Column('strength', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='强弱度(%)')
    activity = Column('activity', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='活跃度(%)')
    avg_turnover = Column('avg_turnover', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='笔换手')
    attack = Column('attack', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='攻击波(%)')
    interval_3 = Column('interval_3', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='近3月涨幅')
    interval_6 = Column('interval_6', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='近6月涨幅')