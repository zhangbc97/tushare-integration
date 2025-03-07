from tushare_models.fx_daily import FxDaily
from tushare_models.fx_obasic import FxObasic

from tushare_integration.spiders.tushare import TimeSeriesSpider, TushareSpider


class FxObasicSpider(TushareSpider):
    """
    外汇基础信息 Spider，用于采集外汇静态基础数据
    """

    __model__: type[FxObasic] = FxObasic


class FxDailySpider(TimeSeriesSpider):
    """
    外汇日线行情 Spider，用于采集外汇日线数据
    """

    __model__: type[FxDaily] = FxDaily
