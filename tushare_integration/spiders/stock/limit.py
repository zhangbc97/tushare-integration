import datetime

from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class DCHotSpider(DailySpider):
    name = "stock/limit/dc_hot"
    api_name = "dc_hot"
    custom_settings = {"TABLE_NAME": "dc_hot", 'MIN_CAL_DATE': '2024-03-20'}

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_scrapy_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req


class HMDetailSpider(DailySpider):
    name = "stock/limit/hm_detail"
    api_name = "hm_detail"
    custom_settings = {"TABLE_NAME": "hm_detail", 'MIN_CAL_DATE': '2022-08-01'}


class HMListSpider(TushareSpider):
    name = "stock/limit/hm_list"
    api_name = "hm_list"
    custom_settings = {"TABLE_NAME": "hm_list"}


class KplConceptConsSpider(DailySpider):
    name = "stock/limit/kpl_concept_cons"
    api_name = "kpl_concept_cons"
    custom_settings = {"TABLE_NAME": "kpl_concept_cons"}


class KplConceptSpider(DailySpider):
    name = "stock/limit/kpl_concept"
    api_name = "kpl_concept"
    custom_settings = {"TABLE_NAME": "kpl_concept"}


class KplListSpider(DailySpider):
    name = "stock/limit/kpl_list"
    api_name = "kpl_list"
    custom_settings = {"TABLE_NAME": "kpl_list"}


class LimitCptListSpider(DailySpider):
    name = "stock/limit/limit_cpt_list"
    api_name = "limit_cpt_list"
    custom_settings = {"TABLE_NAME": "limit_cpt_list"}


class LimitListDSpider(DailySpider):
    name = "stock/limit/limit_list_d"
    api_name = "limit_list_d"
    custom_settings = {"TABLE_NAME": "limit_list_d"}


class LimitListTHSSpider(DailySpider):
    name = "stock/limit/limit_list_ths"
    api_name = "limit_list_ths"
    custom_settings = {"TABLE_NAME": "limit_list_ths"}


class LimitStepSpider(DailySpider):
    name = "stock/limit/limit_step"
    api_name = "limit_step"
    custom_settings = {"TABLE_NAME": "limit_step"}


class THSHotSpider(DailySpider):
    name = "stock/limit/ths_hot"
    api_name = "ths_hot"
    custom_settings = {"TABLE_NAME": "ths_hot", "MIN_CAL_DATE": "2020-01-01"}

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_scrapy_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req
