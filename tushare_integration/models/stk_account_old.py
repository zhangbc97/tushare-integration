# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class StkAccountOld(Base):
    """股票开户数据(旧)"""

    __tablename__: str = 'stk_account_old'
    __api_id__: ClassVar[int] = 165
    __api_name__: ClassVar[str] = 'stk_account_old'
    __api_title__: ClassVar[str] = '股票开户数据(旧)'
    __api_info_title__: ClassVar[str] = '股票账户开户数据(旧)'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '参考数据', '股票开户数据（旧）']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 17, 165]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'start_date': {'type': 'str', 'required': False, 'description': '开始日期'},
        'end_date': {'type': 'str', 'required': False, 'description': '结束日期'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '股票开户数据(旧)',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    date = Column('date', String(), nullable=False, default="", server_default=text("''"), comment='统计周期')
    new_sh = Column(
        'new_sh', Integer, nullable=False, default=0, server_default=text("'0'"), comment='本周新增(上海，户)'
    )
    new_sz = Column(
        'new_sz', Integer, nullable=False, default=0, server_default=text("'0'"), comment='本周新增(深圳，户)'
    )
    active_sh = Column(
        'active_sh',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='期末有效账户(上海，万户)',
    )
    active_sz = Column(
        'active_sz',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='期末有效账户(深圳，万户)',
    )
    total_sh = Column(
        'total_sh', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期末账户数(上海，万户)'
    )
    total_sz = Column(
        'total_sz', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期末账户数(深圳，万户)'
    )
    trade_sh = Column(
        'trade_sh',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='参与交易账户数(上海，万户)',
    )
    trade_sz = Column(
        'trade_sz',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='参与交易账户数(深圳，万户)',
    )
