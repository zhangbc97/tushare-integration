import datetime

from tushare_integration.models.dc_hot import DcHot
from tushare_integration.models.hm_detail import HmDetail
from tushare_integration.models.hm_list import HmList
from tushare_integration.models.kpl_concept import KplConcept
from tushare_integration.models.kpl_concept_cons import KplConceptCons
from tushare_integration.models.kpl_list import KplList
from tushare_integration.models.limit_cpt_list import LimitCptList
from tushare_integration.models.limit_list_d import LimitListD
from tushare_integration.models.limit_list_ths import LimitListThs
from tushare_integration.models.limit_step import LimitStep
from tushare_integration.models.ths_hot import ThsHot
from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class DCHotSpider(DailySpider):

    __model__: type[DcHot] = DcHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_scrapy_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req


class HMDetailSpider(DailySpider):

    __model__: type[HmDetail] = HmDetail


class HMListSpider(TushareSpider):

    __model__: type[HmList] = HmList


class KplConceptConsSpider(DailySpider):

    __model__: type[KplConceptCons] = KplConceptCons


class KplConceptSpider(DailySpider):

    __model__: type[KplConcept] = KplConcept


class KplListSpider(DailySpider):

    __model__: type[KplList] = KplList


class LimitCptListSpider(DailySpider):

    __model__: type[LimitCptList] = LimitCptList


class LimitListDSpider(DailySpider):

    __model__: type[LimitListD] = LimitListD


class LimitListTHSSpider(DailySpider):

    __model__: type[LimitListThs] = LimitListThs


class LimitStepSpider(DailySpider):

    __model__: type[LimitStep] = LimitStep


class THSHotSpider(DailySpider):

    __model__: type[ThsHot] = ThsHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_scrapy_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req
