# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class Coinlist(Base):
    """全球数字货币列表"""

    __tablename__: str = 'coinlist'
    __api_id__: ClassVar[int] = 54
    __api_name__: ClassVar[str] = 'coinlist'
    __api_title__: ClassVar[str] = '全球数字货币列表'
    __api_info_title__: ClassVar[str] = '全球数字货币列表'
    __api_path__: ClassVar[List[str]] = ['另类数据', '基础数据', '全球数字货币列表']
    __api_path_ids__: ClassVar[List[int]] = [41, 3, 54]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'issue_date': {'type': 'str', 'required': False, 'description': '发行日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '结束日期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '全球数字货币列表',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    coin = Column('coin', String(), nullable=False, default="", server_default=text("''"), comment='货币代码')
    en_name = Column('en_name', String(), nullable=False, default="", server_default=text("''"), comment='英文名称')
    cn_name = Column('cn_name', String(), nullable=False, default="", server_default=text("''"), comment='中文名称')
    issue_date = Column('issue_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='发行日期')
    issue_price = Column('issue_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='发行价格(美元)')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='发行总量')
    supply = Column('supply', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通总量')
    algo = Column('algo', String(), nullable=False, default="", server_default=text("''"), comment='算法原理')
    area = Column('area', String(), nullable=False, default="", server_default=text("''"), comment='发行地区')
    desc = Column('desc', String(), nullable=False, default="", server_default=text("''"), comment='描述')
    labels = Column('labels', String(), nullable=False, default="", server_default=text("''"), comment='标签分类')