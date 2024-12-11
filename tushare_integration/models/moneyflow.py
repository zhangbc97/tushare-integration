# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Moneyflow(Base):
    """个股资金流向"""

    __tablename__: str = 'moneyflow'
    __api_id__: ClassVar[int] = 170
    __api_name__: ClassVar[str] = 'moneyflow'
    __api_title__: ClassVar[str] = '个股资金流向'
    __api_info_title__: ClassVar[str] = '个股资金流向'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '资金流向数据', '个股资金流向']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 342, 170]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = ['stock_basic', 'trade_cal']
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'},
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
            'comment': '个股资金流向',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='TS代码')
    trade_date = Column(
        'trade_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='交易日期',
    )
    buy_sm_vol = Column(
        'buy_sm_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='小单买入量(手)'
    )
    buy_sm_amount = Column(
        'buy_sm_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='小单买入金额(万元)'
    )
    sell_sm_vol = Column(
        'sell_sm_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='小单卖出量(手)'
    )
    sell_sm_amount = Column(
        'sell_sm_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='小单卖出金额(万元)'
    )
    buy_md_vol = Column(
        'buy_md_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='中单买入量(手)'
    )
    buy_md_amount = Column(
        'buy_md_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='中单买入金额(万元)'
    )
    sell_md_vol = Column(
        'sell_md_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='中单卖出量(手)'
    )
    sell_md_amount = Column(
        'sell_md_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='中单卖出金额(万元)'
    )
    buy_lg_vol = Column(
        'buy_lg_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='大单买入量(手)'
    )
    buy_lg_amount = Column(
        'buy_lg_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='大单买入金额(万元)'
    )
    sell_lg_vol = Column(
        'sell_lg_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='大单卖出量(手)'
    )
    sell_lg_amount = Column(
        'sell_lg_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='大单卖出金额(万元)'
    )
    buy_elg_vol = Column(
        'buy_elg_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='特大单买入量(手)'
    )
    buy_elg_amount = Column(
        'buy_elg_amount',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='特大单买入金额(万元)',
    )
    sell_elg_vol = Column(
        'sell_elg_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='特大单卖出量(手)'
    )
    sell_elg_amount = Column(
        'sell_elg_amount',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='特大单卖出金额(万元)',
    )
    net_mf_vol = Column(
        'net_mf_vol', Integer, nullable=False, default=0, server_default=text("'0'"), comment='净流入量(手)'
    )
    net_mf_amount = Column(
        'net_mf_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='净流入额(万元)'
    )
    trade_count = Column(
        'trade_count', Integer, nullable=False, default=0, server_default=text("'0'"), comment='交易笔数'
    )
