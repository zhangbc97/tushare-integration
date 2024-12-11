# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class RepoDaily(Base):
    """债券回购日行情"""

    __tablename__: str = 'repo_daily'
    __api_id__: ClassVar[int] = 256
    __api_name__: ClassVar[str] = 'repo_daily'
    __api_title__: ClassVar[str] = '债券回购日行情'
    __api_info_title__: ClassVar[str] = '债券回购日行情'
    __api_path__: ClassVar[List[str]] = ['数据接口', '债券', '债券回购日行情']
    __api_path_ids__: ClassVar[List[int]] = [2, 184, 256]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': 'TS代码'}, 'trade_date': {'type': 'str', 'required': False, 'description': '交易日期(YYYYMMDD格式，下同)'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '结束日期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '债券回购日行情',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='TS代码')
    trade_date = Column('trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='交易日期')
    repo_maturity = Column('repo_maturity', String(), nullable=False, default="", server_default=text("''"), comment='期限品种')
    pre_close = Column('pre_close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='前收盘(%)')
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘价(%)')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最高价(%)')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最低价(%)')
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='收盘价(%)')
    weight = Column('weight', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='加权价(%)')
    weight_r = Column('weight_r', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='加权价(利率债)(%)')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交金额(万元)')
    num = Column('num', Integer, nullable=False, default=0, server_default=text("'0'"), comment='成交笔数(笔)')