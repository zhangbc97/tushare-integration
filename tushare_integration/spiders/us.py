from tushare_models.us_basic import UsBasic
from tushare_models.us_daily import UsDaily
from tushare_models.us_daily_adj import UsDailyAdj
from tushare_models.us_tradecal import UsTradecal

from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider


class UsBasicSpider(TushareSpider):
    __model__: type[UsBasic] = UsBasic


class UsTradecalSpider(LimitOffsetSpider):
    __model__: type[UsTradecal] = UsTradecal


class UsDailySpider(TimeSeriesSpider):
    __model__: type[UsDaily] = UsDaily
    __trade_cal_model__: type[UsTradecal] = UsTradecal


class UsDailyAdjSpider(TimeSeriesSpider):
    __model__: type[UsDailyAdj] = UsDailyAdj
    __trade_cal_model__: type[UsTradecal] = UsTradecal
