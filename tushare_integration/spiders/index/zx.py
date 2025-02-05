from tushare_integration.models.ci_daily import CiDaily
from tushare_integration.spiders.tushare import TimeSeriesSpider


class CIDaily(TimeSeriesSpider):
    __model__: type[CiDaily] = CiDaily
