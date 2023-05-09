from tushare_integration.spiders.tushare import DailySpider


class MarginSpider(DailySpider):
    name = "stock/market/margin"
    custom_settings = {"TABLE_NAME": "margin", 'MIN_CAL_DATE': '2010-01-01'}


class MarginDetailSpider(DailySpider):
    name = "stock/market/margin_detail"
    custom_settings = {"TABLE_NAME": "margin_detail", 'MIN_CAL_DATE': '2010-01-01'}
