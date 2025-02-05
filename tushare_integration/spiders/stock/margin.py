from tushare_integration.models.margin import Margin
from tushare_integration.models.margin_detail import MarginDetail
from tushare_integration.models.margin_secs import MarginSecs
from tushare_integration.models.slb_len_mm import SlbLenMm
from tushare_integration.models.slb_sec import SlbSec
from tushare_integration.models.slb_sec_detail import SlbSecDetail
from tushare_integration.spiders.tushare import TimeSeriesSpider


class MarginSpider(TimeSeriesSpider):
    __model__: type[Margin] = Margin


class MarginDetailSpider(TimeSeriesSpider):
    __model__: type[MarginDetail] = MarginDetail


class MarginSecsSpider(TimeSeriesSpider):
    __model__: type[MarginSecs] = MarginSecs


class SLBLenMMSpider(TimeSeriesSpider):
    __model__: type[SlbLenMm] = SlbLenMm


class SLBSecDetailSpider(TimeSeriesSpider):
    __model__: type[SlbSecDetail] = SlbSecDetail


class SLBSecSpider(TimeSeriesSpider):
    __model__: type[SlbSec] = SlbSec
