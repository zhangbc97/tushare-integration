# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class UsTbr(Base):
    """短期国债利率"""

    __tablename__: str = 'us_tbr'
    __api_id__: ClassVar[int] = 221
    __api_name__: ClassVar[str] = 'us_tbr'
    __api_title__: ClassVar[str] = '短期国债利率'
    __api_info_title__: ClassVar[str] = '短期国债利率'
    __api_path__: ClassVar[List[str]] = ['数据接口', '宏观经济', '国际宏观', '美国利率', '短期国债利率']
    __api_path_ids__: ClassVar[List[int]] = [2, 147, 217, 218, 221]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'date': {'type': 'str', 'required': False, 'description': '日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '结束日期'}, 'fields': {'type': 'str', 'required': False, 'description': '指定字段'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '短期国债利率',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    date = Column('date', String(), nullable=False, default="", server_default=text("''"), comment='日期')
    w4_bd = Column('w4_bd', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='4周银行折现收益率')
    w4_ce = Column('w4_ce', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='4周票面利率')
    w8_bd = Column('w8_bd', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='8周银行折现收益率')
    w8_ce = Column('w8_ce', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='8周票面利率')
    w13_bd = Column('w13_bd', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='13周银行折现收益率')
    w13_ce = Column('w13_ce', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='13周票面利率')
    w26_bd = Column('w26_bd', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='26周银行折现收益率')
    w26_ce = Column('w26_ce', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='26周票面利率')
    w52_bd = Column('w52_bd', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='52周银行折现收益率')
    w52_ce = Column('w52_ce', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='52周票面利率')