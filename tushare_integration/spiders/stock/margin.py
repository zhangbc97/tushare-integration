from tushare_integration.models.margin import Margin
from tushare_integration.models.margin_detail import MarginDetail
from tushare_integration.models.slb_len_mm import SlbLenMm
from tushare_integration.models.slb_sec import SlbSec
from tushare_integration.models.slb_sec_detail import SlbSecDetail
from tushare_integration.spiders.tushare import DailySpider, FinancialReportSpider, TSCodeSpider, TushareSpider


class MarginSpider(DailySpider):

    __model__: type[Margin] = Margin


class MarginDetailSpider(DailySpider):

    __model__: type[MarginDetail] = MarginDetail


class SLBLenMMSpider(DailySpider):

    __model__: type[SlbLenMm] = SlbLenMm


class SLBSecDetailSpider(DailySpider):

    __model__: type[SlbSecDetail] = SlbSecDetail


class SLBSecSpider(DailySpider):

    __model__: type[SlbSec] = SlbSec
