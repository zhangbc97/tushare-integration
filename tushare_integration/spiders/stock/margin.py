from tushare_models.margin import Margin
from tushare_models.margin_detail import MarginDetail
from tushare_models.margin_secs import MarginSecs
from tushare_models.slb_len import SlbLen
from tushare_models.slb_len_mm import SlbLenMm
from tushare_models.slb_sec import SlbSec
from tushare_models.slb_sec_detail import SlbSecDetail

from tushare_integration.spiders.tushare import TimeSeriesSpider


class MarginSpider(TimeSeriesSpider):
    __model__: type[Margin] = Margin


class MarginDetailSpider(TimeSeriesSpider):
    __model__: type[MarginDetail] = MarginDetail


class MarginSecsSpider(TimeSeriesSpider):
    __model__: type[MarginSecs] = MarginSecs


class SLBSecSpider(TimeSeriesSpider):
    __model__: type[SlbSec] = SlbSec


class SLBLenSpider(TimeSeriesSpider):
    __model__: type[SlbLen] = SlbLen


class SLBSecDetailSpider(TimeSeriesSpider):
    __model__: type[SlbSecDetail] = SlbSecDetail


class SLBLenMMSpider(TimeSeriesSpider):
    __model__: type[SlbLenMm] = SlbLenMm
