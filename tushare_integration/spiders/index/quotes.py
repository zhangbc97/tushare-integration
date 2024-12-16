import datetime

from sqlalchemy import select

from tushare_integration.models.daily_info import DailyInfo
from tushare_integration.models.index_basic import IndexBasic
from tushare_integration.models.index_daily import IndexDaily
from tushare_integration.models.index_dailybasic import IndexDailybasic
from tushare_integration.models.index_global import IndexGlobal
from tushare_integration.models.index_monthly import IndexMonthly
from tushare_integration.models.index_weekly import IndexWeekly
from tushare_integration.models.index_weight import IndexWeight
from tushare_integration.models.sz_daily_info import SzDailyInfo
from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class IndexDailySpider(DailySpider):
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

                yield self.get_scrapy_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": start_date.strftime("%Y%m%d"),
                        "end_date": end_date.strftime("%Y%m%d"),
                    }
                )
                start_date = end_date
                end_date = start_date + datetime.timedelta(days=30 * 365)


class DailyInfoSpider(DailySpider):
    __model__: type[DailyInfo] = DailyInfo


# noinspection SpellCheckingInspection
class IndexDailyBasicSpider(DailySpider):
    __model__: type[IndexDailybasic] = IndexDailybasic


class IndexGlobalSpider(DailySpider):
    __model__: type[IndexGlobal] = IndexGlobal


# 创建指数专用的基类
class IndexWeeklySpider(TushareSpider):
    __model__: type[IndexWeekly] = IndexWeekly


class IndexMonthlySpider(IndexWeeklySpider):
    __model__: type[IndexMonthly] = IndexMonthly


class IndexWeightSpider(TushareSpider):
    __model__: type[IndexWeight] = IndexWeight


class SZDailyInfoSpider(DailySpider):
    __model__: type[SzDailyInfo] = SzDailyInfo
