# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class IndexDailybasic(Base):
    """大盘指数每日指标"""

    __tablename__: str = 'index_dailybasic'
    __api_id__: ClassVar[int] = 128
    __api_name__: ClassVar[str] = 'index_dailybasic'
    __api_title__: ClassVar[str] = '大盘指数每日指标'
    __api_info_title__: ClassVar[str] = '大盘指数每日指标'
    __api_path__: ClassVar[List[str]] = ['数据接口', '指数', '大盘指数每日指标']
    __api_path_ids__: ClassVar[List[int]] = [2, 93, 128]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'trade_date': {'type': 'str', 'required': False, 'description': '交易日期'},
        'ts_code': {'type': 'str', 'required': False, 'description': 'TS指数代码'},
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
            'comment': '大盘指数每日指标',
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
    total_mv = Column(
        'total_mv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日总市值'
    )
    float_mv = Column(
        'float_mv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日流通市值'
    )
    total_share = Column(
        'total_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日总股本'
    )
    float_share = Column(
        'float_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日流通股本'
    )
    free_share = Column(
        'free_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日自由流通股本'
    )
    turnover_rate = Column(
        'turnover_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='换手率'
    )
    turnover_rate_f = Column(
        'turnover_rate_f',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='换手率(自由流通股本)',
    )
    pe = Column('pe', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='市盈率')
    pe_ttm = Column('pe_ttm', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='市盈率TTM')
    pb = Column('pb', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='市净率')
