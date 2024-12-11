# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class FundManager(Base):
    """基金经理"""

    __tablename__: str = 'fund_manager'
    __api_id__: ClassVar[int] = 208
    __api_name__: ClassVar[str] = 'fund_manager'
    __api_title__: ClassVar[str] = '基金经理'
    __api_info_title__: ClassVar[str] = '基金经理'
    __api_path__: ClassVar[List[str]] = ['数据接口', '公募基金', '基金经理']
    __api_path_ids__: ClassVar[List[int]] = [2, 18, 208]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': '基金代码'}, 'ann_date': {'type': 'str', 'required': False, 'description': '公告日期'}, 'name': {'type': 'str', 'required': False, 'description': '基金经理姓名'}, 'offset': {'type': 'int', 'required': False, 'description': '开始行数'}, 'limit': {'type': 'int', 'required': False, 'description': '每页行数'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '基金经理',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='基金代码')
    ann_date = Column('ann_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='公告日期')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='基金经理姓名')
    gender = Column('gender', String(), nullable=False, default="", server_default=text("''"), comment='性别')
    birth_year = Column('birth_year', String(), nullable=False, default="", server_default=text("''"), comment='出生年份')
    edu = Column('edu', String(), nullable=False, default="", server_default=text("''"), comment='学历')
    nationality = Column('nationality', String(), nullable=False, default="", server_default=text("''"), comment='国籍')
    begin_date = Column('begin_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='任职日期')
    end_date = Column('end_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='历任日期')
    resume = Column('resume', String(), nullable=False, default="", server_default=text("''"), comment='简历')