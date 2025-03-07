import datetime
from typing import Literal

from sqlalchemy import select
from tushare_models.ci_daily import CiDaily
from tushare_models.daily_info import DailyInfo
from tushare_models.idx_factor_pro import IdxFactorPro
from tushare_models.index_basic import IndexBasic
from tushare_models.index_classify import IndexClassify
from tushare_models.index_daily import IndexDaily
from tushare_models.index_dailybasic import IndexDailybasic
from tushare_models.index_global import IndexGlobal
from tushare_models.index_member_all import IndexMemberAll
from tushare_models.index_monthly import IndexMonthly
from tushare_models.index_weekly import IndexWeekly
from tushare_models.index_weight import IndexWeight
from tushare_models.sw_daily import SwDaily
from tushare_models.sz_daily_info import SzDailyInfo
from tushare_models.ths_daily import ThsDaily

from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider


class IndexBasicSpider(TushareSpider):
    __model__: type[IndexBasic] = IndexBasic

    def start_requests(self):
        markets = ["MSCI", "CSI", "SSE", "SZSE", "CICC", "SW", "OTH"]

        for market in markets:
            params = {"market": market}
            yield self.get_httpx_request(params)


class IndexDailySpider(TimeSeriesSpider):
    __model__: type[IndexDaily] = IndexDaily

    def start_requests(self):
        # index_daily需要特殊处理，这个接口不支持按日期获取数据，这意味着需要用ts_code去取
        # 接口一次性最大返回8000条数据，部分指数的数据量超过8000条，所以需要分批取
        # 到2024年最多的一年只有257个交易日，我们按一年260个交易日来计算，一次可以取30年的数据
        # 看了一下实际上现在就3000多个指数，全请求一次也就不到8000次，直接全量取吧
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有指数
        query = select(IndexBasic)
        index_list = conn.query_df(query)

        if index_list.empty:
            return

        # 从base_date开始取，一次+30年
        for _, row in index_list.iterrows():
            ts_code = row["ts_code"]
            start_date = row["base_date"].date()
            end_date = start_date + datetime.timedelta(days=30 * 365)

            while True:
                if start_date > datetime.date.today():
                    break

                yield self.get_httpx_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": start_date.strftime("%Y%m%d"),
                        "end_date": end_date.strftime("%Y%m%d"),
                    }
                )
                start_date = end_date
                end_date = start_date + datetime.timedelta(days=30 * 365)


class IndexWeeklySpider(TimeSeriesSpider):
    __model__: type[IndexWeekly] = IndexWeekly
    __trade_date_period__: Literal["D", "W", "ME"] = 'W'


class IndexMonthlySpider(TimeSeriesSpider):
    __model__: type[IndexMonthly] = IndexMonthly
    __trade_date_period__: Literal["D", "W", "ME"] = 'ME'


class IndexWeightSpider(LimitOffsetSpider, TimeSeriesSpider):
    __model__: type[IndexWeight] = IndexWeight

    def start_requests(self):
        for trade_date in self.get_trade_dates('D'):
            yield self.get_httpx_request(params={"trade_date": trade_date})


class IndexDailyBasicSpider(TimeSeriesSpider):
    __model__: type[IndexDailybasic] = IndexDailybasic


class IndexClassifySpider(TushareSpider):
    __model__: type[IndexClassify] = IndexClassify


class IndexMemberAllSpider(LimitOffsetSpider):
    __model__: type[IndexMemberAll] = IndexMemberAll
    __limit__: int = 3000


class DailyInfoSpider(TimeSeriesSpider):
    __model__: type[DailyInfo] = DailyInfo


class SZDailyInfoSpider(TimeSeriesSpider):
    __model__: type[SzDailyInfo] = SzDailyInfo


class THSDailySpider(TimeSeriesSpider):
    __model__: type[ThsDaily] = ThsDaily


class CIDaily(TimeSeriesSpider):
    __model__: type[CiDaily] = CiDaily


class SWDailySpider(TimeSeriesSpider):
    __model__: type[SwDaily] = SwDaily

    def start_requests(self):
        conn = self.get_db_engine()

        query = select(IndexClassify.index_code).distinct()
        df = conn.query_df(query)

        if df.empty:
            return

        for index_code in df['index_code']:
            yield self.get_httpx_request(params={"index_code": index_code})


class IndexGlobalSpider(TimeSeriesSpider):
    __model__: type[IndexGlobal] = IndexGlobal


class IdxFactorProSpider(TimeSeriesSpider):
    __model__: type[IdxFactorPro] = IdxFactorPro
