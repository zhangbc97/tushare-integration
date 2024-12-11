# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class Suspend(Base):
    """停复牌"""

    __tablename__: str = 'suspend'
    __api_id__: ClassVar[int] = 31
    __api_name__: ClassVar[str] = 'suspend'
    __api_title__: ClassVar[str] = '停复牌'
    __api_info_title__: ClassVar[str] = '停复牌'
    __api_path__: ClassVar[List[str]] = ['停复牌']
    __api_path_ids__: ClassVar[List[int]] = []
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'},
        'suspend_date': {'type': 'str', 'required': False, 'description': '停牌日期'},
        'resume_date': {'type': 'str', 'required': False, 'description': '复牌日期'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '停复牌',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    suspend_date = Column(
        'suspend_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='停牌日期',
    )
    resume_date = Column(
        'resume_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='复牌日期',
    )
    ann_date = Column(
        'ann_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='公告日期'
    )
    suspend_reason = Column(
        'suspend_reason', String(), nullable=False, default="", server_default=text("''"), comment='停牌原因'
    )
    reason_type = Column(
        'reason_type', String(), nullable=False, default="", server_default=text("''"), comment='停牌原因类别'
    )
    suspend_timing = Column(
        'suspend_timing', String(), nullable=False, default="", server_default=text("''"), comment='停牌时间段'
    )
