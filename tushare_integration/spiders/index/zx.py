from tushare_integration.spiders.tushare import DailySpider


class CIDaily(DailySpider):
    name = "index/zx/ci_daily"
    custom_settings = {"TABLE_NAME": "ci_daily"}
