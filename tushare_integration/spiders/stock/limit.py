import datetime

from tushare_models.dc_hot import DcHot
from tushare_models.dc_index import DcIndex
from tushare_models.dc_member import DcMember
from tushare_models.hm_detail import HmDetail
from tushare_models.hm_list import HmList
from tushare_models.kpl_concept import KplConcept
from tushare_models.kpl_concept_cons import KplConceptCons
from tushare_models.kpl_list import KplList
from tushare_models.limit_cpt_list import LimitCptList
from tushare_models.limit_list_d import LimitListD
from tushare_models.limit_list_ths import LimitListThs
from tushare_models.limit_step import LimitStep
from tushare_models.ths_hot import ThsHot
from tushare_models.ths_index import ThsIndex
from tushare_models.ths_member import ThsMember
from tushare_models.top_inst import TopInst
from tushare_models.top_list import TopList

from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


class KplConceptSpider(TimeSeriesSpider):
    __model__: type[KplConcept] = KplConcept


class KplConceptConsSpider(TimeSeriesSpider):
    __model__: type[KplConceptCons] = KplConceptCons


class KplListSpider(TimeSeriesSpider):
    __model__: type[KplList] = KplList


class TopListSpider(TimeSeriesSpider):
    __model__: type[TopList] = TopList


class TopInstSpider(TimeSeriesSpider):
    __model__: type[TopInst] = TopInst


class LimitListTHSSpider(TimeSeriesSpider):
    __model__: type[LimitListThs] = LimitListThs


class LimitListDSpider(TimeSeriesSpider):
    __model__: type[LimitListD] = LimitListD


class LimitStepSpider(TimeSeriesSpider):
    __model__: type[LimitStep] = LimitStep


class LimitCptListSpider(TimeSeriesSpider):
    __model__: type[LimitCptList] = LimitCptList


class THSIndexSpider(LimitOffsetSpider):
    __model__: type[ThsIndex] = ThsIndex


class THSMemberSpider(TSCodeSpider):
    __model__: type[ThsMember] = ThsMember
    __basic_table__: type[ThsIndex] = ThsIndex


class DcIndexSpider(TimeSeriesSpider):
    __model__: type[DcIndex] = DcIndex


class DcMemberSpider(TimeSeriesSpider):
    __model__: type[DcMember] = DcMember


class HMListSpider(TushareSpider):
    __model__: type[HmList] = HmList


class HMDetailSpider(TimeSeriesSpider):
    __model__: type[HmDetail] = HmDetail


class THSHotSpider(TimeSeriesSpider):
    __model__: type[ThsHot] = ThsHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_httpx_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req


class DCHotSpider(TimeSeriesSpider):
    __model__: type[DcHot] = DcHot

    def start_requests(self):
        # 每次都先更新当天的，直接忽略历史数据，然后更新历史数据
        yield self.get_httpx_request(params={'trade_date': datetime.datetime.now().strftime("%Y%m%d")})
        for req in super().start_requests():
            yield req
