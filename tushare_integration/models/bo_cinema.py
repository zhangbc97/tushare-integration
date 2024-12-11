# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class BoCinema(Base):
    """影院日度票房"""

    __tablename__: str = 'bo_cinema'
    __api_id__: ClassVar[int] = 116
    __api_name__: ClassVar[str] = 'bo_cinema'
    __api_title__: ClassVar[str] = '影院日度票房'
    __api_info_title__: ClassVar[str] = '影院每日票房'
    __api_path__: ClassVar[List[str]] = ['数据接口', '行业经济', 'TMT行业', '影院日度票房']
    __api_path_ids__: ClassVar[List[int]] = [2, 82, 83, 116]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'date': {'type': 'str', 'required': True, 'description': '日期'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '影院日度票房',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    date = Column('date', String(), nullable=False, default="", server_default=text("''"), comment='日期')
    c_name = Column('c_name', String(), nullable=False, default="", server_default=text("''"), comment='影院名称')
    aud_count = Column('aud_count', Integer, nullable=False, default=0, server_default=text("'0'"), comment='观众人数')
    att_ratio = Column('att_ratio', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='上座率')
    day_amount = Column(
        'day_amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日票房'
    )
    day_showcount = Column(
        'day_showcount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='当日场次'
    )
    avg_price = Column(
        'avg_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='场均票价(元)'
    )
    p_pc = Column('p_pc', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='场均人次')
    rank = Column('rank', Integer, nullable=False, default=0, server_default=text("'0'"), comment='排名')
