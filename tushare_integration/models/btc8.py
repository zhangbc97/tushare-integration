# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Btc8(Base):
    """巴比特"""

    __tablename__: str = 'btc8'
    __api_id__: ClassVar[int] = 71
    __api_name__: ClassVar[str] = 'btc8'
    __api_title__: ClassVar[str] = '巴比特'
    __api_info_title__: ClassVar[str] = '巴比特'
    __api_path__: ClassVar[List[str]] = ['另类数据', '资讯公告', '巴比特']
    __api_path_ids__: ClassVar[List[int]] = [41, 69, 71]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['url']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'start_date': {'type': 'datetime', 'required': True, 'description': '开始时间'},
        'end_date': {'type': 'datetime', 'required': True, 'description': '结束时间'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '巴比特',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    title = Column('title', String(), nullable=False, default="", server_default=text("''"), comment='标题')
    content = Column('content', String(), nullable=False, default="", server_default=text("''"), comment='内容')
    type = Column('type', String(), nullable=False, default="", server_default=text("''"), comment='类型')
    url = Column('url', String(), nullable=False, default="", server_default=text("''"), comment='URL')
    datetime = Column('datetime', String(), nullable=False, default="", server_default=text("''"), comment='时间')
