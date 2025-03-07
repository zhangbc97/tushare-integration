from tushare_models.sge_basic import SgeBasic
from tushare_models.sge_daily import SgeDaily

from tushare_integration.spiders.tushare import TimeSeriesSpider, TushareSpider


# 现货基础信息 Spider，采集上海黄金基础信息
class SgeBasicSpider(TushareSpider):
    __model__ = SgeBasic


# 现货日行情 Spider，采集上海黄金现货日行情
class SgeDailySpider(TimeSeriesSpider):
    __model__ = SgeDaily
