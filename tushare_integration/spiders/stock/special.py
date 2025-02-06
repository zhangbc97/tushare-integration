import datetime

from sqlalchemy import and_, distinct, func, not_, select

from tushare_integration.models.broker_recommend import BrokerRecommend
from tushare_integration.models.ccass_hold import CcassHold
from tushare_integration.models.ccass_hold_detail import CcassHoldDetail
from tushare_integration.models.cyq_chips import CyqChips
from tushare_integration.models.cyq_perf import CyqPerf
from tushare_integration.models.daily import Daily
from tushare_integration.models.hk_hold import HkHold
from tushare_integration.models.report_rc import ReportRc
from tushare_integration.models.stk_auction_c import StkAuctionC
from tushare_integration.models.stk_auction_o import StkAuctionO
from tushare_integration.models.stk_factor import StkFactor
from tushare_integration.models.stk_factor_pro import StkFactorPro
from tushare_integration.models.stk_nineturn import StkNineturn
from tushare_integration.models.stk_surv import StkSurv
from tushare_integration.models.stock_basic import StockBasic
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


class ReportRCSpider(TimeSeriesSpider):
    __model__: type[ReportRc] = ReportRc


class CyqPerfSpider(TimeSeriesSpider):
    __model__: type[CyqPerf] = CyqPerf


class CyqChipsSpider(TushareSpider):
    __model__: type[CyqChips] = CyqChips

    def start_requests(self):
        conn = self.get_db_engine()

        # 获取所有股票代码
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            # 构建子查询：获取已有的交易日期
            subquery = select(distinct(self.__model__.trade_date)).where(self.__model__.ts_code == ts_code)

            # 构建主查询：获取在 daily 中出现但在 cyq_chips 中没有的交易日期
            query = select(distinct(Daily.trade_date)).where(
                and_(
                    Daily.ts_code == ts_code, Daily.trade_date >= self.start_date, not_(Daily.trade_date.in_(subquery))
                )
            )

            trade_dates = conn.query_df(query)

            if trade_dates.empty:
                continue

            for trade_date in trade_dates['trade_date'].dt.date:
                yield self.get_httpx_request({"ts_code": ts_code, "trade_date": trade_date.strftime("%Y%m%d")})


class StkFactorSpider(TimeSeriesSpider):
    __model__: type[StkFactor] = StkFactor


class StkFactorProSpider(TimeSeriesSpider):
    __model__: type[StkFactorPro] = StkFactorPro


class CCASSHoldSpider(TimeSeriesSpider):
    __model__: type[CcassHold] = CcassHold


class CCASSHoldDetailSpider(TimeSeriesSpider):
    __model__: type[CcassHoldDetail] = CcassHoldDetail


class HKHoldSpider(TimeSeriesSpider):
    __model__: type[HkHold] = HkHold


class StkAuctionOSpider(TimeSeriesSpider):
    __model__: type[StkAuctionO] = StkAuctionO


class StkAuctionCSpider(TimeSeriesSpider):
    __model__: type[StkAuctionC] = StkAuctionC


class StkNineturnSpider(LimitOffsetSpider):
    __model__: type[StkNineturn] = StkNineturn
    __limit__: int = 10000

    def start_requests(self):
        # 获取所有股票代码
        conn = self.get_db_engine()
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        # 对每个 ts_code 分别请求日线和60分钟数据，全量采集，配合limit+offset分页处理
        for ts_code in ts_codes:
            for freq in ["daily", "60min"]:
                params = {
                    "ts_code": ts_code,
                    "freq": freq,
                    "limit": self.__limit__,
                    "offset": 0,
                }
                yield self.get_httpx_request(params)


class StkSurvSpider(LimitOffsetSpider):
    __model__: type[StkSurv] = StkSurv
    __limit__: int = 100

    def start_requests(self):
        # 获取所有股票代码
        conn = self.get_db_engine()
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            yield self.get_httpx_request({"ts_code": ts_code})


class BrokerRecommendSpider(TushareSpider):
    __model__: type[BrokerRecommend] = BrokerRecommend

    def start_requests(self):
        for year in range(2020, datetime.datetime.now().year + 1):
            for month in range(1, 13):
                yield self.get_httpx_request({"month": f"{year}{month:02d}"})
