from tushare_integration.models.ci_daily import CiDaily
from tushare_integration.spiders.tushare import DailySpider


class CIDaily(DailySpider):
    __spider_name__ = "index/zx/ci_daily"
    __model__: type[CiDaily] = CiDaily
