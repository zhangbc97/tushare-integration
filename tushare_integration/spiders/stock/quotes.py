from tushare_integration.spiders.tushare import DailySpider


class StockDailySpider(DailySpider):
    name = "stock/quotes/daily"
    custom_settings = {"TABLE_NAME": "daily"}


class AdjFactorSpider(DailySpider):
    name = "stock/quotes/adj_factor"
    custom_settings = {"TABLE_NAME": "adj_factor"}


class SuspendDSpider(DailySpider):
    name = "stock/quotes/suspend_d"
    custom_settings = {"TABLE_NAME": "suspend_d"}


class HSGTTop10Spider(DailySpider):
    name = "stock/quotes/hsgt_top10"
    custom_settings = {"TABLE_NAME": "hsgt_top10"}


class MoneyFlowSpider(DailySpider):
    name = "stock/quotes/moneyflow"
    custom_settings = {"TABLE_NAME": "moneyflow"}


class MoneyFlowHSGTSpider(DailySpider):
    name = "stock/quotes/moneyflow_hsgt"
    custom_settings = {"TABLE_NAME": "moneyflow_hsgt"}


class StkLimitSpider(DailySpider):
    name = "stock/quotes/stk_limit"
    custom_settings = {"TABLE_NAME": "stk_limit", 'MIN_CAL_DATE': '2007-01-01'}
