# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class HkBasic(Base):
    """港股基础信息"""

    __tablename__: str = 'hk_basic'
    __api_id__: ClassVar[int] = 191
    __api_name__: ClassVar[str] = 'hk_basic'
    __api_title__: ClassVar[str] = '港股基础信息'
    __api_info_title__: ClassVar[str] = '港股列表'
    __api_path__: ClassVar[List[str]] = ['数据接口', '港股', '港股基础信息']
    __api_path_ids__: ClassVar[List[int]] = [2, 190, 191]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': 'TS代码'},
        'list_status': {'type': 'str', 'required': False, 'description': '上市状态 L上市 D退市 P暂停上市'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '港股基础信息',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='股票简称')
    fullname = Column('fullname', String(), nullable=False, default="", server_default=text("''"), comment='公司全称')
    enname = Column('enname', String(), nullable=False, default="", server_default=text("''"), comment='英文名称')
    cn_spell = Column('cn_spell', String(), nullable=False, default="", server_default=text("''"), comment='拼音')
    market = Column('market', String(), nullable=False, default="", server_default=text("''"), comment='市场类别')
    list_status = Column(
        'list_status', String(), nullable=False, default="", server_default=text("''"), comment='上市状态'
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
    trade_unit = Column(
        'trade_unit', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='交易单位'
    )
    isin = Column('isin', String(), nullable=False, default="", server_default=text("''"), comment='ISIN代码')
    curr_type = Column('curr_type', String(), nullable=False, default="", server_default=text("''"), comment='货币代码')
