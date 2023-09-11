from tushare_integration.spiders.stock.quotes import StockMonthlySpider, StockWeeklySpider
from tushare_integration.spiders.tushare import DailySpider


class IndexDailySpider(DailySpider):
    name = "index/quotes/index_daily"
    custom_settings = {"TABLE_NAME": "index_daily"}


class DailyInfoSpider(DailySpider):
    name = "index/quotes/daily_info"
    custom_settings = {"TABLE_NAME": "daily_info"}


# noinspection SpellCheckingInspection
class IndexDailyBasicSpider(DailySpider):
    name = "index/quotes/index_dailybasic"
    custom_settings = {"TABLE_NAME": "index_dailybasic"}


class IndexGlobalSpider(DailySpider):
    name = "index/quotes/index_global"
    custom_settings = {"TABLE_NAME": "index_global"}


class IndexMonthlySpider(StockMonthlySpider):
    name = "index/quotes/index_monthly"
    custom_settings = {"TABLE_NAME": "index_monthly"}


class IndexWeeklySpider(StockWeeklySpider):
    name = "index/quotes/index_weekly"
    custom_settings = {"TABLE_NAME": "index_weekly"}


class IndexWeightSpider(StockMonthlySpider):
    name = "index/quotes/index_weight"
    custom_settings = {"TABLE_NAME": "index_weight"}


class SzDailyInfoSpider(DailySpider):
    name = "index/quotes/sz_daily_info"
    custom_settings = {"TABLE_NAME": "sz_daily_info"}
