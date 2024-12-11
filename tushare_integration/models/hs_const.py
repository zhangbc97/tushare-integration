# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class HsConst(Base):
    """沪深股通成分股"""

    __tablename__: str = 'hs_const'
    __api_id__: ClassVar[int] = 104
    __api_name__: ClassVar[str] = 'hs_const'
    __api_title__: ClassVar[str] = '沪深股通成分股'
    __api_info_title__: ClassVar[str] = '沪深股通成份股'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '基础数据', '沪深股通成分股']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 24, 104]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'hs_type': {'type': 'str', 'required': True, 'description': '类型SH沪股通SZ深股通'}, 'is_new': {'type': 'str', 'required': False, 'description': '是否最新1最新0不是'}, 'ts_code': {'type': 'str', 'required': False, 'description': 'ts_code'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '沪深股通成分股',
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
    hs_type = Column('hs_type', String(), nullable=False, default="", server_default=text("''"), comment='沪深港通类型SH沪SZ深')
    in_date = Column('in_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='纳入日期')
    out_date = Column('out_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='剔除日期')
    is_new = Column('is_new', String(), nullable=False, default="", server_default=text("''"), comment='是否最新')