# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Coincap(Base):
    """数字货币每日市值"""

    __tablename__: str = 'coincap'
    __api_id__: ClassVar[int] = 57
    __api_name__: ClassVar[str] = 'coincap'
    __api_title__: ClassVar[str] = '数字货币每日市值'
    __api_info_title__: ClassVar[str] = '数字货币每日市值'
    __api_path__: ClassVar[List[str]] = ['另类数据', '行情数据', '数字货币每日市值']
    __api_path_ids__: ClassVar[List[int]] = [41, 52, 57]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'trade_date': {'type': 'str', 'required': True, 'description': '日期'},
        'coin': {'type': 'str', 'required': False, 'description': 'coin代码'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '数字货币每日市值',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    trade_date = Column(
        'trade_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='交易日期',
    )
    coin = Column('coin', String(), nullable=False, default="", server_default=text("''"), comment='货币代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='货币名称')
    marketcap = Column(
        'marketcap', String(), nullable=False, default="", server_default=text("''"), comment='市值(美元)'
    )
    price = Column(
        'price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当前时间价格(美元)'
    )
    vol24 = Column(
        'vol24', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='24小时成交额(美元)'
    )
    supply = Column('supply', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通总量')
    create_time = Column(
        'create_time', String(), nullable=False, default="", server_default=text("''"), comment='数据采集时间'
    )