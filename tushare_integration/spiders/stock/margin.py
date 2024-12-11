from tushare_integration.models.margin import Margin
from tushare_integration.models.margin_detail import MarginDetail
from tushare_integration.models.slb_len_mm import SlbLenMm
from tushare_integration.models.slb_sec import SlbSec
from tushare_integration.models.slb_sec_detail import SlbSecDetail
from tushare_integration.spiders.tushare import DailySpider, FinancialReportSpider, TSCodeSpider, TushareSpider


class MarginSpider(DailySpider):
    name = "stock/margin/margin"
    __model__: type[Margin] = Margin


class MarginDetailSpider(DailySpider):
    name = "stock/margin/margin_detail"
    __model__: type[MarginDetail] = MarginDetail


class SLBLenMMSpider(DailySpider):
    name = "stock/margin/slb_len_mm"
    __model__: type[SlbLenMm] = SlbLenMm


class SLBSecDetailSpider(DailySpider):
    name = "stock/margin/slb_sec_detail"
    __model__: type[SlbSecDetail] = SlbSecDetail


class SLBSecSpider(DailySpider):
    name = "stock/margin/slb_sec"
    __model__: type[SlbSec] = SlbSec
