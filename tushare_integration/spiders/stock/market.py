from sqlalchemy import select
from tushare_models.block_trade import BlockTrade
from tushare_models.concept import Concept
from tushare_models.concept_detail import ConceptDetail
from tushare_models.pledge_detail import PledgeDetail
from tushare_models.pledge_stat import PledgeStat
from tushare_models.repurchase import Repurchase
from tushare_models.share_float import ShareFloat
from tushare_models.stk_holdernumber import StkHoldernumber
from tushare_models.stk_holdertrade import StkHoldertrade
from tushare_models.top10_floatholders import Top10Floatholders
from tushare_models.top10_holders import Top10Holders

from tushare_integration.spiders.tushare import FinancialReportSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


class Top10HoldersSpider(FinancialReportSpider):
    __model__: type[Top10Holders] = Top10Holders


class Top10FloatHoldersSpider(FinancialReportSpider):
    __model__: type[Top10Floatholders] = Top10Floatholders


class PledgeStatSpider(TSCodeSpider):
    __model__: type[PledgeStat] = PledgeStat


class PledgeDetailSpider(TSCodeSpider):
    __model__: type[PledgeDetail] = PledgeDetail


class RepurchaseSpider(TSCodeSpider):
    __model__: type[Repurchase] = Repurchase


class ConceptSpider(TushareSpider):
    __model__: type[Concept] = Concept


class ConceptDetailSpider(TSCodeSpider):
    __model__: type[ConceptDetail] = ConceptDetail

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 concept code
        query = select(Concept.code)
        codes = conn.query_df(query)['code']

        for code in codes:
            yield self.get_httpx_request(params={'id': code})


class ShareFloatSpider(TSCodeSpider):
    __model__: type[ShareFloat] = ShareFloat


class BlockTradeSpider(TimeSeriesSpider):
    __model__: type[BlockTrade] = BlockTrade


class StkHoldernumberSpider(TimeSeriesSpider):
    __model__: type[StkHoldernumber] = StkHoldernumber
    __trade_date_field__: str = "ann_date"


class StkHoldertradeSpider(TimeSeriesSpider):
    __model__: type[StkHoldertrade] = StkHoldertrade
    __trade_date_field__: str = "ann_date"
