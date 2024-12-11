# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class CbBasic(Base):
    """可转债基础信息"""

    __tablename__: str = 'cb_basic'
    __api_id__: ClassVar[int] = 185
    __api_name__: ClassVar[str] = 'cb_basic'
    __api_title__: ClassVar[str] = '可转债基础信息'
    __api_info_title__: ClassVar[str] = '可转债基本信息'
    __api_path__: ClassVar[List[str]] = ['数据接口', '债券', '可转债基础信息']
    __api_path_ids__: ClassVar[List[int]] = [2, 184, 185]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '转债代码'},
        'list_date': {'type': 'str', 'required': False, 'description': '上市日期'},
        'exchange': {'type': 'str', 'required': False, 'description': '上市地点'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '可转债基础信息',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='转债代码')
    bond_full_name = Column(
        'bond_full_name', String(), nullable=False, default="", server_default=text("''"), comment='转债名称'
    )
    bond_short_name = Column(
        'bond_short_name', String(), nullable=False, default="", server_default=text("''"), comment='转债简称'
    )
    cb_code = Column('cb_code', String(), nullable=False, default="", server_default=text("''"), comment='转股申报代码')
    stk_code = Column('stk_code', String(), nullable=False, default="", server_default=text("''"), comment='正股代码')
    stk_short_name = Column(
        'stk_short_name', String(), nullable=False, default="", server_default=text("''"), comment='正股简称'
    )
    maturity = Column(
        'maturity', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='发行期限(年)'
    )
    par = Column('par', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='面值')
    issue_price = Column(
        'issue_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='发行价格'
    )
    issue_size = Column(
        'issue_size', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='发行总额(元)'
    )
    remain_size = Column(
        'remain_size', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='债券余额(元)'
    )
    value_date = Column(
        'value_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='起息日期',
    )
    maturity_date = Column(
        'maturity_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='到期日期',
    )
    rate_type = Column('rate_type', String(), nullable=False, default="", server_default=text("''"), comment='利率类型')
    coupon_rate = Column(
        'coupon_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='票面利率(%)'
    )
    add_rate = Column(
        'add_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='补偿利率(%)'
    )
    pay_per_year = Column(
        'pay_per_year', Integer, nullable=False, default=0, server_default=text("'0'"), comment='年付息次数'
    )
    list_date = Column(
        'list_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='上市日期'
    )
    delist_date = Column(
        'delist_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='摘牌日'
    )
    exchange = Column('exchange', String(), nullable=False, default="", server_default=text("''"), comment='上市地点')
    conv_start_date = Column(
        'conv_start_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='转股起始日',
    )
    conv_end_date = Column(
        'conv_end_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='转股截止日',
    )
    conv_stop_date = Column(
        'conv_stop_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='停止转股日(提前到期)',
    )
    first_conv_price = Column(
        'first_conv_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='初始转股价'
    )
    conv_price = Column(
        'conv_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最新转股价'
    )
    rate_clause = Column(
        'rate_clause', String(), nullable=False, default="", server_default=text("''"), comment='利率说明'
    )
    put_clause = Column(
        'put_clause', String(), nullable=False, default="", server_default=text("''"), comment='赎回条款'
    )
    maturity_put_price = Column(
        'maturity_put_price',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='到期赎回价格(含税)',
    )
    call_clause = Column(
        'call_clause', String(), nullable=False, default="", server_default=text("''"), comment='回售条款'
    )
    reset_clause = Column(
        'reset_clause', String(), nullable=False, default="", server_default=text("''"), comment='特别向下修正条款'
    )
    conv_clause = Column(
        'conv_clause', String(), nullable=False, default="", server_default=text("''"), comment='转股条款'
    )
    guarantor = Column('guarantor', String(), nullable=False, default="", server_default=text("''"), comment='担保人')
    guarantee_type = Column(
        'guarantee_type', String(), nullable=False, default="", server_default=text("''"), comment='担保方式'
    )
    issue_rating = Column(
        'issue_rating', String(), nullable=False, default="", server_default=text("''"), comment='发行信用等级'
    )
    newest_rating = Column(
        'newest_rating', String(), nullable=False, default="", server_default=text("''"), comment='最新信用等级'
    )
    rating_comp = Column(
        'rating_comp', String(), nullable=False, default="", server_default=text("''"), comment='最新评级机构'
    )