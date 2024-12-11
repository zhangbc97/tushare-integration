# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class SlbSec(Base):
    """转融券交易汇总"""

    __tablename__: str = 'slb_sec'
    __api_id__: ClassVar[int] = 332
    __api_name__: ClassVar[str] = 'slb_sec'
    __api_title__: ClassVar[str] = '转融券交易汇总'
    __api_info_title__: ClassVar[str] = '转融券交易汇总'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '两融及转融通', '转融券交易汇总']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 330, 332]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'trade_date': {'type': 'str', 'required': False, 'description': '交易日期（YYYYMMDD格式，下同）'}, 'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'}, 'start_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '开始日期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '转融券交易汇总',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    trade_date = Column('trade_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='交易日期(YYYYMMDD)')
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='股票代码')
    name = Column('name', String(), nullable=False, default="", server_default=text("''"), comment='股票名称')
    ope_inv = Column('ope_inv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期初余量(万股)')
    lent_qnt = Column('lent_qnt', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='转融券融出数量(万股)')
    cls_inv = Column('cls_inv', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期末余量(万股)')
    end_bal = Column('end_bal', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期末余额(万元)')