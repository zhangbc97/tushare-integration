from tushare_integration.spiders.tushare import DailySpider
from tushare_integration.models.ci_daily import CiDaily


class CIDaily(DailySpider):
    name = "index/zx/ci_daily"
    __model__: type[CiDaily] = CiDaily
