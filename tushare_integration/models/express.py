# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using black

from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class Express(Base):
    """业绩快报"""

    __tablename__: str = 'express'
    __api_id__: ClassVar[int] = 46
    __api_name__: ClassVar[str] = 'express'
    __api_title__: ClassVar[str] = '业绩快报'
    __api_info_title__: ClassVar[str] = '业绩快报'
    __api_path__: ClassVar[List[str]] = ['数据接口', '沪深股票', '财务数据', '业绩快报']
    __api_path_ids__: ClassVar[List[int]] = [2, 14, 16, 46]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = []
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {'ts_code': {'type': 'str', 'required': False, 'description': '股票代码'}, 'ann_date': {'type': 'str', 'required': False, 'description': '公告日期'}, 'start_date': {'type': 'str', 'required': False, 'description': '公告开始日期'}, 'end_date': {'type': 'str', 'required': False, 'description': '公告结束日期'}, 'period': {'type': 'str', 'required': False, 'description': '报告期'}, 'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'}, 'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'}}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '业绩快报',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    
    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='TS股票代码')
    ann_date = Column('ann_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='公告日期')
    end_date = Column('end_date', Date, nullable=False, default="1970-01-01", server_default=text("'1970-01-01'"), comment='报告期')
    revenue = Column('revenue', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='营业收入(元)')
    operate_profit = Column('operate_profit', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='营业利润(元)')
    total_profit = Column('total_profit', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='利润总额(元)')
    n_income = Column('n_income', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='净利润(元)')
    total_assets = Column('total_assets', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='总资产(元)')
    total_hldr_eqy_exc_min_int = Column('total_hldr_eqy_exc_min_int', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='股东权益合计(不含少数股东权益)(元)')
    diluted_eps = Column('diluted_eps', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='每股收益(摊薄)(元)')
    diluted_roe = Column('diluted_roe', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='净资产收益率(摊薄)(%)')
    yoy_net_profit = Column('yoy_net_profit', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期修正后净利润')
    bps = Column('bps', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='每股净资产')
    yoy_sales = Column('yoy_sales', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增长率:营业收入')
    yoy_op = Column('yoy_op', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增长率:营业利润')
    yoy_tp = Column('yoy_tp', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增长率:利润总额')
    yoy_dedu_np = Column('yoy_dedu_np', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增长率:归属母公司股东的净利润')
    yoy_eps = Column('yoy_eps', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增长率:基本每股收益')
    yoy_roe = Column('yoy_roe', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='同比增减:加权平均净资产收益率')
    growth_assets = Column('growth_assets', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='比年初增长率:总资产')
    yoy_equity = Column('yoy_equity', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='比年初增长率:归属母公司的股东权益')
    growth_bps = Column('growth_bps', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='比年初增长率:归属于母公司股东的每股净资产')
    or_last_year = Column('or_last_year', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期营业收入')
    op_last_year = Column('op_last_year', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期营业利润')
    tp_last_year = Column('tp_last_year', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期利润总额')
    np_last_year = Column('np_last_year', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期净利润')
    eps_last_year = Column('eps_last_year', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='去年同期每股收益')
    open_net_assets = Column('open_net_assets', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期初净资产')
    open_bps = Column('open_bps', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='期初每股净资产')
    perf_summary = Column('perf_summary', String(), nullable=False, default="", server_default=text("''"), comment='业绩简要说明')
    is_audit = Column('is_audit', Integer, nullable=False, default=0, server_default=text("'0'"), comment='是否审计： 1是 0否')
    remark = Column('remark', String(), nullable=False, default="", server_default=text("''"), comment='备注')
    update_flag = Column('update_flag', String(), nullable=False, default="", server_default=text("''"), comment='更新标志')