# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Coinexchanges(Base):
    """全球数字货币交易所"""

    __tablename__: str = 'coinexchanges'
    __api_id__: ClassVar[int] = 66
    __api_name__: ClassVar[str] = 'coinexchanges'
    __api_title__: ClassVar[str] = '全球数字货币交易所'
    __api_info_title__: ClassVar[str] = '全球数字货币交易所'
    __api_path__: ClassVar[List[str]] = ['另类数据', '基础数据', '全球数字货币交易所']
    __api_path_ids__: ClassVar[List[int]] = [41, 3, 66]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'exchange': {'type': 'str', 'required': False, 'description': '交易所'},
        'area_code': {'type': 'str', 'required': False, 'description': '地区'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '全球数字货币交易所',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    exchange = Column('exchange', String(), nullable=False, default="", server_default=text("''"), comment='交易所代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='交易所名称')
    pairs = Column('pairs', Integer, nullable=False, default=0, server_default=text("'0'"), comment='交易对数量')
    area_code = Column(
        'area_code', String(), nullable=False, default="", server_default=text("''"), comment='所在地区代码'
    )
    area = Column('area', String(), nullable=False, default="", server_default=text("''"), comment='所在地区')
    coin_trade = Column(
        'coin_trade', String(), nullable=False, default="", server_default=text("''"), comment='支持现货交易'
    )
    fut_trade = Column(
        'fut_trade', String(), nullable=False, default="", server_default=text("''"), comment='支持期货交易'
    )
    oct_trade = Column(
        'oct_trade', String(), nullable=False, default="", server_default=text("''"), comment='支持场外交易'
    )
    deep_share = Column(
        'deep_share', String(), nullable=False, default="", server_default=text("''"), comment='支持共享交易深度'
    )
    mineable = Column(
        'mineable', String(), nullable=False, default="", server_default=text("''"), comment='支持挖矿交易'
    )
    desc = Column('desc', String(), nullable=False, default="", server_default=text("''"), comment='交易所简介')
    website = Column('website', String(), nullable=False, default="", server_default=text("''"), comment='交易所官网')
    twitter = Column(
        'twitter', String(), nullable=False, default="", server_default=text("''"), comment='交易所twitter'
    )
    facebook = Column(
        'facebook', String(), nullable=False, default="", server_default=text("''"), comment='交易所facebook'
    )
    weibo = Column('weibo', String(), nullable=False, default="", server_default=text("''"), comment='交易所weibo')
