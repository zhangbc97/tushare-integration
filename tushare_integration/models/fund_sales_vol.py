# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class FundSalesVol(Base):
    """销售机构公募基金销售保有规模"""

    __tablename__: str = 'fund_sales_vol'
    __api_id__: ClassVar[int] = 266
    __api_name__: ClassVar[str] = 'fund_sales_vol'
    __api_title__: ClassVar[str] = '销售机构公募基金销售保有规模'
    __api_info_title__: ClassVar[str] = '销售机构公募基金销售保有规模'
    __api_path__: ClassVar[List[str]] = ['数据接口', '财富管理', '基金销售行业数据', '销售机构公募基金销售保有规模']
    __api_path_ids__: ClassVar[List[int]] = [2, 263, 264, 266]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'year': {'type': 'str', 'required': False, 'description': '年度'}, 'quarter': {'type': 'str', 'required': False, 'description': '季度'}, 'name': {'type': 'str', 'required': False, 'description': '机构名称'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '销售机构公募基金销售保有规模',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    year = Column('year', Integer, nullable=False, default=0, server_default=text("'0'"), comment='年度')
    quarter = Column('quarter', String(), nullable=False, default="", server_default=text("''"), comment='季度')
    inst_name = Column('inst_name', String(), nullable=False, default="", server_default=text("''"), comment='销售机构')
    fund_scale = Column('fund_scale', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='股票+混合公募基金保有规模(亿元)')
    scale = Column('scale', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='非货币市场公募基金保有规模(亿元)')
    rank = Column('rank', Integer, nullable=False, default=0, server_default=text("'0'"), comment='排名')