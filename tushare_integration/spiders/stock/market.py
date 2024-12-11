from tushare_integration.spiders.tushare import DailySpider, FinancialReportSpider, TSCodeSpider, TushareSpider
from tushare_integration.models.margin_secs import MarginSecs
from tushare_integration.models.top10_holders import Top10Holders
from tushare_integration.models.top10_floatholders import Top10Floatholders
from tushare_integration.models.top_list import TopList
from tushare_integration.models.top_inst import TopInst
from tushare_integration.models.pledge_stat import PledgeStat
from tushare_integration.models.pledge_detail import PledgeDetail
from tushare_integration.models.repurchase import Repurchase
from tushare_integration.models.share_float import ShareFloat
from tushare_integration.models.concept import Concept
from tushare_integration.models.concept_detail import ConceptDetail
from tushare_integration.models.block_trade import BlockTrade
from tushare_integration.models.stk_holdernumber import StkHoldernumber
from tushare_integration.models.stk_holdertrade import StkHoldertrade
from sqlalchemy import select


class MarginSecsSpider(DailySpider):
    name = "stock/market/margin_secs"
    __model__: type[MarginSecs] = MarginSecs


class Top10HoldersSpider(FinancialReportSpider):
    name = "stock/market/top10_holders"
    __model__: type[Top10Holders] = Top10Holders
    custom_settings = {"HAS_VIP": False}


class Top10FloatHoldersSpider(FinancialReportSpider):
    name = "stock/market/top10_floatholders"
    __model__: type[Top10Floatholders] = Top10Floatholders
    custom_settings = {"HAS_VIP": False}


class TopListSpider(DailySpider):
    name = "stock/market/top_list"
    __model__: type[TopList] = TopList


class TopInstSpider(DailySpider):
    name = "stock/market/top_inst"
    __model__: type[TopInst] = TopInst


class PledgeStatSpider(TSCodeSpider):
    name = "stock/market/pledge_stat"
    __model__: type[PledgeStat] = PledgeStat
    custom_settings = {"BASIC_TABLE": "stock_basic"}


class PledgeDetailSpider(TSCodeSpider):
    name = "stock/market/pledge_detail"
    __model__: type[PledgeDetail] = PledgeDetail
    custom_settings = {"BASIC_TABLE": "stock_basic"}


class RepurchaseSpider(TSCodeSpider):
    name = "stock/market/repurchase"
    __model__: type[Repurchase] = Repurchase
    custom_settings = {"BASIC_TABLE": "stock_basic"}


class ShareFloatSpider(TSCodeSpider):
    name = "stock/market/share_float"
    __model__: type[ShareFloat] = ShareFloat
    custom_settings = {"BASIC_TABLE": "stock_basic"}


class ConceptSpider(TushareSpider):
    name = "stock/market/concept"
    __model__: type[Concept] = Concept


class ConceptDetailSpider(TSCodeSpider):
    name = "stock/market/concept_detail"
    __model__: type[ConceptDetail] = ConceptDetail

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 concept code
        query = select(Concept.code)
        codes = conn.query_df(query)['code']

        for code in codes:
            yield self.get_scrapy_request(params={'id': code})


class BlockTradeSpider(DailySpider):
    name = "stock/market/block_trade"
    __model__: type[BlockTrade] = BlockTrade


class StkHoldernumberSpider(DailySpider):
    name = "stock/market/stk_holdernumber"
    __model__: type[StkHoldernumber] = StkHoldernumber
    custom_settings = {"TRADE_DATE_FIELD": "ann_date"}


class StkHoldertradeSpider(DailySpider):
    name = "stock/market/stk_holdertrade"
    __model__: type[StkHoldertrade] = StkHoldertrade
    custom_settings = {"TRADE_DATE_FIELD": "ann_date"}
