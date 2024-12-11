# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class UsBasic(Base):
    """美股基础信息"""

    __tablename__: str = 'us_basic'
    __api_id__: ClassVar[int] = 252
    __api_name__: ClassVar[str] = 'us_basic'
    __api_title__: ClassVar[str] = '美股基础信息'
    __api_info_title__: ClassVar[str] = '美股列表'
    __api_path__: ClassVar[List[str]] = ['数据接口', '美股', '美股基础信息']
    __api_path_ids__: ClassVar[List[int]] = [2, 251, 252]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '股票代码（e.g. AAPL）'},
        'classify': {'type': 'str', 'required': False, 'description': '股票分类（ADR/GDR/EQ）'},
        'list_stauts': {'type': 'str', 'required': False, 'description': '上市状态'},
        'offset': {'type': 'str', 'required': False, 'description': '开始行数'},
        'limit': {'type': 'str', 'required': False, 'description': '每页最大行数'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '美股基础信息',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='美股代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='中文名称')
    enname = Column('enname', String(), nullable=False, default="", server_default=text("''"), comment='英文名称')
    classify = Column(
        'classify', String(), nullable=False, default="", server_default=text("''"), comment='分类ADR/GDR/EQ'
    )
    list_status = Column(
        'list_status',
        String(),
        nullable=False,
        default="",
        server_default=text("''"),
        comment='上市状态L上市D退市P暂停上市',
    )
    list_date = Column(
        'list_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='上市日期'
    )
    delist_date = Column(
        'delist_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='退市日期',
    )