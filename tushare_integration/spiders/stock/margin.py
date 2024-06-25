from tushare_integration.spiders.tushare import DailySpider, FinancialReportSpider, TSCodeSpider, TushareSpider


class MarginSpider(DailySpider):
    name = "stock/margin/margin"
    api_name = "margin"
    custom_settings = {"TABLE_NAME": "margin", 'MIN_CAL_DATE': '2010-01-01'}


class MarginDetailSpider(DailySpider):
    name = "stock/margin/margin_detail"
    api_name = "margin_detail"
    custom_settings = {"TABLE_NAME": "margin_detail", 'MIN_CAL_DATE': '2010-01-01'}


class SLBLenMM(DailySpider):
    name = "stock/margin/slb_len_mm"
    api_name = "slb_len_mm"
    custom_settings = {"TABLE_NAME": "slb_len_mm", 'MIN_CAL_DATE': '2022-11-14'}


class SLBLen(TushareSpider):
    # 一把梭直接取完就行
    name = "stock/margin/slb_len"
    api_name = "slb_len"
    custom_settings = {"TABLE_NAME": "slb_len"}


class SLBSecDetail(DailySpider):
    name = "stock/margin/slb_sec_detail"
    api_name = "slb_sec_detail"
    custom_settings = {"TABLE_NAME": "slb_sec_detail", 'MIN_CAL_DATE': '2019-07-22'}


class SLBSec(DailySpider):
    name = "stock/margin/slb_sec"
    api_name = "slb_sec"
    custom_settings = {"TABLE_NAME": "slb_sec", 'MIN_CAL_DATE': '2013-02-28'}
