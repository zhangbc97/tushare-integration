# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class BcOtcqt(Base):
    """柜台流通式债券报价"""

    __tablename__: str = 'bc_otcqt'
    __api_id__: ClassVar[int] = 322
    __api_name__: ClassVar[str] = 'bc_otcqt'
    __api_title__: ClassVar[str] = '柜台流通式债券报价'
    __api_info_title__: ClassVar[str] = '柜台流通式债券报价'
    __api_path__: ClassVar[List[str]] = ['数据接口', '债券', '柜台流通式债券报价']
    __api_path_ids__: ClassVar[List[int]] = [2, 184, 322]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'trade_date': {'type': 'str', 'required': False, 'description': ''},
        'start_date': {'type': 'str', 'required': False, 'description': ''},
        'end_date': {'type': 'str', 'required': False, 'description': ''},
        'ts_code': {'type': 'str', 'required': False, 'description': ''},
        'bank': {'type': 'str', 'required': False, 'description': ''},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '柜台流通式债券报价',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    trade_date = Column(
        'trade_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='报价日期',
    )
    qt_time = Column('qt_time', String(), nullable=False, default="", server_default=text("''"), comment='报价时间')
    bank = Column('bank', String(), nullable=False, default="", server_default=text("''"), comment='报价机构')
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='债券编码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='债券简称')
    maturity = Column('maturity', String(), nullable=False, default="", server_default=text("''"), comment='期限')
    remain_maturity = Column(
        'remain_maturity', String(), nullable=False, default="", server_default=text("''"), comment='剩余期限'
    )
    bond_type = Column('bond_type', String(), nullable=False, default="", server_default=text("''"), comment='债券类型')
    coupon_rate = Column(
        'coupon_rate', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='票面利率(%)'
    )
    buy_price = Column(
        'buy_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='投资者买入全价'
    )
    sell_price = Column(
        'sell_price', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='投资者卖出全价'
    )
    buy_yield = Column(
        'buy_yield', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='投资者买入到期收益率(%)'
    )
    sell_yield = Column(
        'sell_yield',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='投资者卖出到期收益率(%)',
    )