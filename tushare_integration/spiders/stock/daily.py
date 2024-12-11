from tushare_integration.spiders.tushare import DailySpider
from tushare_integration.models.daily import Daily
from tushare_integration.models.daily_basic import DailyBasic
from tushare_integration.models.adj_factor import AdjFactor
from tushare_integration.models.suspend_d import SuspendD
from tushare_integration.models.hsgt_top10 import HsgtTop10
from tushare_integration.models.limit_list import LimitList
from tushare_integration.models.moneyflow import Moneyflow
from tushare_integration.models.stk_limit import StkLimit


class StockDailySpider(DailySpider):
    name = "stock/daily/daily"
    __model__: type[Daily] = Daily


class DailyBasicSpider(DailySpider):
    name = "stock/daily/daily_basic"
    __model__: type[DailyBasic] = DailyBasic


class AdjFactorSpider(DailySpider):
    name = "stock/daily/adj_factor"
    __model__: type[AdjFactor] = AdjFactor


class SuspendDSpider(DailySpider):
    name = "stock/daily/suspend_d"
    __model__: type[SuspendD] = SuspendD


class HSGTTop10Spider(DailySpider):
    name = "stock/daily/hsgt_top10"
    __model__: type[HsgtTop10] = HsgtTop10


class LimitListSpider(DailySpider):
    name = "stock/daily/limit_list"
    __model__: type[LimitList] = LimitList


class MoneyFlowSpider(DailySpider):
    name = "stock/daily/moneyflow"
    __model__: type[Moneyflow] = Moneyflow


class StkLimitSpider(DailySpider):
    name = "stock/daily/stk_limit"
    __model__: type[StkLimit] = StkLimit
