# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class ShareFloat(Base):
    """限售股解禁"""

    __tablename__: str = 'share_float'
    __api_id__: ClassVar[int] = 160
    __api_name__: ClassVar[str] = 'share_float'
    __api_title__: ClassVar[str] = '限售股解禁'
    __api_info_title__: ClassVar[str] = '限售股解禁'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '参考数据', '限售股解禁']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 17, 160]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': 'TS股票代码'}, 'ann_date': {'type': 'str', 'required': False, 'description': '公告日期'}, 'float_date': {'type': 'str', 'required': False, 'description': '解禁日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '解禁开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '解禁结束日期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '限售股解禁',
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
    ann_date = Column('ann_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='公告日期')
    float_date = Column('float_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='解禁日期')
    float_share = Column('float_share', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通股份')
    float_ratio = Column('float_ratio', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='流通股份占总股本比率')
    holder_name = Column('holder_name', String(), nullable=False, default="", server_default=text("''"), comment='股东名称')
    share_type = Column('share_type', String(), nullable=False, default="", server_default=text("''"), comment='股份类型')