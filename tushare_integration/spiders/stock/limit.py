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
from tushare_integration.models.top_inst import TopInst
from tushare_integration.models.top_list import TopList
from tushare_integration.spiders.tushare import TimeSeriesSpider, TushareSpider


class DCHotSpider(TimeSeriesSpider):
    __model__: type[DcHot] = DcHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_httpx_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req


class HMDetailSpider(TimeSeriesSpider):
    __model__: type[HmDetail] = HmDetail


class HMListSpider(TushareSpider):
    __model__: type[HmList] = HmList


class KplConceptConsSpider(TimeSeriesSpider):
    __model__: type[KplConceptCons] = KplConceptCons


class KplConceptSpider(TimeSeriesSpider):
    __model__: type[KplConcept] = KplConcept


class KplListSpider(TimeSeriesSpider):
    __model__: type[KplList] = KplList


class LimitCptListSpider(TimeSeriesSpider):
    __model__: type[LimitCptList] = LimitCptList


class LimitListDSpider(TimeSeriesSpider):
    __model__: type[LimitListD] = LimitListD


class LimitListTHSSpider(TimeSeriesSpider):
    __model__: type[LimitListThs] = LimitListThs


class LimitStepSpider(TimeSeriesSpider):
    __model__: type[LimitStep] = LimitStep


class THSHotSpider(TimeSeriesSpider):
    __model__: type[ThsHot] = ThsHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_httpx_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req


class TopListSpider(TimeSeriesSpider):
    __model__: type[TopList] = TopList


class TopInstSpider(TimeSeriesSpider):
    __model__: type[TopInst] = TopInst
