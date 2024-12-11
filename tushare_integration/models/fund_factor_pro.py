# This file is auto-generated by generate_models.py
# This file may be manually edited after generation
# The file has been formatted using isort and black

from typing import Any, ClassVar, Dict, List

from clickhouse_sqlalchemy import engines
from sqlalchemy import Column, text

from tushare_integration.models.core import Base, Date, DateTime, Float, Integer, String


class FundFactorPro(Base):
    """基金技术面因子(专业版)"""

    __tablename__: str = 'fund_factor_pro'
    __api_id__: ClassVar[int] = 359
    __api_name__: ClassVar[str] = 'fund_factor_pro'
    __api_title__: ClassVar[str] = '基金技术面因子(专业版)'
    __api_info_title__: ClassVar[str] = '场内基金技术因子(专业版)'
    __api_path__: ClassVar[List[str]] = ['数据接口', '公募基金', '基金技术面因子(专业版)']
    __api_path_ids__: ClassVar[List[int]] = [2, 18, 359]
    __api_points_required__: ClassVar[int] = 2000
    __api_special_permission__: ClassVar[bool] = False
    __has_vip__: ClassVar[bool] = False
    __dependencies__: ClassVar[List[str]] = []
    __primary_key__: ClassVar[List[str]] = ['ts_code', 'trade_date']
    __start_date__: ClassVar[str | None] = None
    __end_date__: ClassVar[str | None] = None
    __api_params__: ClassVar[Dict[str, Any]] = {
        'ts_code': {'type': 'str', 'required': False, 'description': '基金代码'},
        'start_date': {'type': 'str', 'required': False, 'description': '开始日期'},
        'end_date': {'type': 'str', 'required': False, 'description': '结束日期'},
        'trade_date': {'type': 'str', 'required': False, 'description': '交易日期'},
        'limit': {'type': 'int', 'required': False, 'description': '单次返回数据长度'},
        'offset': {'type': 'int', 'required': False, 'description': '请求数据的开始位移量'},
    }

    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '基金技术面因子(专业版)',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        },
    )

    ts_code = Column('ts_code', String(16), nullable=False, default="", server_default=text("''"), comment='基金代码')
    trade_date = Column(
        'trade_date',
        Date,
        nullable=False,
        default="1970-01-01",
        server_default=text("'1970-01-01'"),
        comment='交易日期',
    )
    trade_date_doris = Column(
        'trade_date_doris', String(), nullable=False, default="", server_default=text("''"), comment='日期'
    )
    open = Column('open', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='开盘价')
    high = Column('high', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最高价')
    low = Column('low', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='最低价')
    close = Column('close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='收盘价')
    pre_close = Column('pre_close', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='昨收价')
    change = Column('change', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='涨跌额')
    pct_change = Column(
        'pct_change',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='涨跌幅 (未复权，如果是复权请用 通用行情接口 )',
    )
    vol = Column('vol', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交量 (手)')
    amount = Column('amount', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='成交额 (千元)')
    asi_bfq = Column(
        'asi_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10',
    )
    asit_bfq = Column(
        'asit_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='振动升降指标-OPEN, CLOSE, HIGH, LOW, M1=26, M2=10',
    )
    atr_bfq = Column(
        'atr_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='真实波动N日平均值-CLOSE, HIGH, LOW, N=20',
    )
    bbi_bfq = Column(
        'bbi_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BBI多空指标-CLOSE, M1=3, M2=6, M3=12, M4=20',
    )
    bias1_bfq = Column(
        'bias1_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BIAS乖离率-CLOSE, L1=6, L2=12, L3=24',
    )
    bias2_bfq = Column(
        'bias2_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BIAS乖离率-CLOSE, L1=6, L2=12, L3=24',
    )
    bias3_bfq = Column(
        'bias3_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BIAS乖离率-CLOSE, L1=6, L2=12, L3=24',
    )
    boll_lower_bfq = Column(
        'boll_lower_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BOLL指标，布林带-CLOSE, N=20, P=2',
    )
    boll_mid_bfq = Column(
        'boll_mid_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BOLL指标，布林带-CLOSE, N=20, P=2',
    )
    boll_upper_bfq = Column(
        'boll_upper_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='BOLL指标，布林带-CLOSE, N=20, P=2',
    )
    brar_ar_bfq = Column(
        'brar_ar_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26',
    )
    brar_br_bfq = Column(
        'brar_br_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' BRAR情绪指标-OPEN, CLOSE, HIGH, LOW, M1=26',
    )
    cci_bfq = Column(
        'cci_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='顺势指标又叫CCI指标-CLOSE, HIGH, LOW, N=14',
    )
    cr_bfq = Column(
        'cr_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='CR价格动量指标-CLOSE, HIGH, LOW, N=20',
    )
    dfma_dif_bfq = Column(
        'dfma_dif_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='平行线差指标-CLOSE, N1=10, N2=50, M=10',
    )
    dfma_difma_bfq = Column(
        'dfma_difma_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='平行线差指标-CLOSE, N1=10, N2=50, M=10',
    )
    dmi_adx_bfq = Column(
        'dmi_adx_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6',
    )
    dmi_adxr_bfq = Column(
        'dmi_adxr_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6',
    )
    dmi_mdi_bfq = Column(
        'dmi_mdi_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6',
    )
    dmi_pdi_bfq = Column(
        'dmi_pdi_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment=' 动向指标-CLOSE, HIGH, LOW, M1=14, M2=6',
    )
    downdays = Column('downdays', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='连跌天数')
    updays = Column('updays', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='连涨天数')
    dpo_bfq = Column(
        'dpo_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='区间震荡线-CLOSE, M1=20, M2=10, M3=6',
    )
    madpo_bfq = Column(
        'madpo_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='区间震荡线-CLOSE, M1=20, M2=10, M3=6',
    )
    ema_bfq_10 = Column(
        'ema_bfq_10', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=10'
    )
    ema_bfq_20 = Column(
        'ema_bfq_20', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=20'
    )
    ema_bfq_250 = Column(
        'ema_bfq_250', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=250'
    )
    ema_bfq_30 = Column(
        'ema_bfq_30', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=30'
    )
    ema_bfq_5 = Column(
        'ema_bfq_5', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=5'
    )
    ema_bfq_60 = Column(
        'ema_bfq_60', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=60'
    )
    ema_bfq_90 = Column(
        'ema_bfq_90', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='指数移动平均-N=90'
    )
    emv_bfq = Column(
        'emv_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='简易波动指标-HIGH, LOW, VOL, N=14, M=9',
    )
    maemv_bfq = Column(
        'maemv_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='简易波动指标-HIGH, LOW, VOL, N=14, M=9',
    )
    expma_12_bfq = Column(
        'expma_12_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='EMA指数平均数指标-CLOSE, N1=12, N2=50',
    )
    expma_50_bfq = Column(
        'expma_50_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='EMA指数平均数指标-CLOSE, N1=12, N2=50',
    )
    kdj_bfq = Column(
        'kdj_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3',
    )
    kdj_d_bfq = Column(
        'kdj_d_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3',
    )
    kdj_k_bfq = Column(
        'kdj_k_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='KDJ指标-CLOSE, HIGH, LOW, N=9, M1=3, M2=3',
    )
    ktn_down_bfq = Column(
        'ktn_down_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10',
    )
    ktn_mid_bfq = Column(
        'ktn_mid_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10',
    )
    ktn_upper_bfq = Column(
        'ktn_upper_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='肯特纳交易通道, N选20日，ATR选10日-CLOSE, HIGH, LOW, N=20, M=10',
    )
    lowdays = Column(
        'lowdays',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='LOWRANGE(LOW)表示当前最低价是近多少周期内最低价的最小值',
    )
    topdays = Column(
        'topdays',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='TOPRANGE(HIGH)表示当前最高价是近多少周期内最高价的最大值',
    )
    ma_bfq_10 = Column(
        'ma_bfq_10', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=10'
    )
    ma_bfq_20 = Column(
        'ma_bfq_20', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=20'
    )
    ma_bfq_250 = Column(
        'ma_bfq_250', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=250'
    )
    ma_bfq_30 = Column(
        'ma_bfq_30', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=30'
    )
    ma_bfq_5 = Column(
        'ma_bfq_5', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=5'
    )
    ma_bfq_60 = Column(
        'ma_bfq_60', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=60'
    )
    ma_bfq_90 = Column(
        'ma_bfq_90', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='简单移动平均-N=90'
    )
    macd_bfq = Column(
        'macd_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='MACD指标-CLOSE, SHORT=12, LONG=26, M=9',
    )
    macd_dea_bfq = Column(
        'macd_dea_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='MACD指标-CLOSE, SHORT=12, LONG=26, M=9',
    )
    macd_dif_bfq = Column(
        'macd_dif_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='MACD指标-CLOSE, SHORT=12, LONG=26, M=9',
    )
    mass_bfq = Column(
        'mass_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='梅斯线-HIGH, LOW, N1=9, N2=25, M=6',
    )
    ma_mass_bfq = Column(
        'ma_mass_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='梅斯线-HIGH, LOW, N1=9, N2=25, M=6',
    )
    mfi_bfq = Column(
        'mfi_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='MFI指标是成交量的RSI指标-CLOSE, HIGH, LOW, VOL, N=14',
    )
    mtm_bfq = Column(
        'mtm_bfq', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='动量指标-CLOSE, N=12, M=6'
    )
    mtmma_bfq = Column(
        'mtmma_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='动量指标-CLOSE, N=12, M=6',
    )
    obv_bfq = Column(
        'obv_bfq', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='能量潮指标-CLOSE, VOL'
    )
    psy_bfq = Column(
        'psy_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6',
    )
    psyma_bfq = Column(
        'psyma_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='投资者对股市涨跌产生心理波动的情绪指标-CLOSE, N=12, M=6',
    )
    roc_bfq = Column(
        'roc_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='变动率指标-CLOSE, N=12, M=6',
    )
    maroc_bfq = Column(
        'maroc_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='变动率指标-CLOSE, N=12, M=6',
    )
    rsi_bfq_12 = Column(
        'rsi_bfq_12', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='RSI指标-CLOSE, N=12'
    )
    rsi_bfq_24 = Column(
        'rsi_bfq_24', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='RSI指标-CLOSE, N=24'
    )
    rsi_bfq_6 = Column(
        'rsi_bfq_6', Float, nullable=False, default=0.0, server_default=text("'0.0'"), comment='RSI指标-CLOSE, N=6'
    )
    taq_down_bfq = Column(
        'taq_down_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='唐安奇通道(海龟)交易指标-HIGH, LOW, 20',
    )
    taq_mid_bfq = Column(
        'taq_mid_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='唐安奇通道(海龟)交易指标-HIGH, LOW, 20',
    )
    taq_up_bfq = Column(
        'taq_up_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='唐安奇通道(海龟)交易指标-HIGH, LOW, 20',
    )
    trix_bfq = Column(
        'trix_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='三重指数平滑平均线-CLOSE, M1=12, M2=20',
    )
    trma_bfq = Column(
        'trma_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='三重指数平滑平均线-CLOSE, M1=12, M2=20',
    )
    vr_bfq = Column(
        'vr_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='VR容量比率-CLOSE, VOL, M1=26',
    )
    wr_bfq = Column(
        'wr_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6',
    )
    wr1_bfq = Column(
        'wr1_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='W&R 威廉指标-CLOSE, HIGH, LOW, N=10, N1=6',
    )
    xsii_td1_bfq = Column(
        'xsii_td1_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7',
    )
    xsii_td2_bfq = Column(
        'xsii_td2_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7',
    )
    xsii_td3_bfq = Column(
        'xsii_td3_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7',
    )
    xsii_td4_bfq = Column(
        'xsii_td4_bfq',
        Float,
        nullable=False,
        default=0.0,
        server_default=text("'0.0'"),
        comment='薛斯通道II-CLOSE, HIGH, LOW, N=102, M=7',
    )