# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class MoneyflowThs(Base):
    """个股资金流向(THS)"""

    __tablename__: str = 'moneyflow_ths'
    __api_id__: ClassVar[int] = 348
    __api_name__: ClassVar[str] = 'moneyflow_ths'
    __api_title__: ClassVar[str] = '个股资金流向(THS)'
    __api_info_title__: ClassVar[str] = '个股资金流向(THS)'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '资金流向数据', '个股资金流向（THS）']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 342, 348]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'}, 'trade_date': {'type': 'str', 'required': False, 'description': '交易日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '结束日期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '个股资金流向(THS)',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    trade_date = Column('trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='交易日期')
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='股票名称')
    pct_change = Column('pct_change', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='涨跌幅')
    latest = Column('latest', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最新价')
    net_amount = Column('net_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='资金净流入(万元)')
    net_d5_amount = Column('net_d5_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='5日主力净额(万元)')
    buy_lg_amount = Column('buy_lg_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日大单净流入额(万元)')
    buy_lg_amount_rate = Column('buy_lg_amount_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日大单净流入占比(%)')
    buy_md_amount = Column('buy_md_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日中单净流入额(万元)')
    buy_md_amount_rate = Column('buy_md_amount_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日中单净流入占比(%)')
    buy_sm_amount = Column('buy_sm_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日小单净流入额(万元)')
    buy_sm_amount_rate = Column('buy_sm_amount_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='今日小单净流入占比(%)')