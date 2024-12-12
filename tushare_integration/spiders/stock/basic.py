from sqlalchemy import not_, select

from tushare_integration.models.hs_const import HsConst
from tushare_integration.models.namechange import Namechange
from tushare_integration.models.stk_managers import StkManagers
from tushare_integration.models.stk_rewards import StkRewards
from tushare_integration.models.stock_basic import StockBasic
from tushare_integration.models.stock_company import StockCompany
from tushare_integration.models.trade_cal import TradeCal
from tushare_integration.spiders.tushare import TushareSpider


class StockBasicSpider(TushareSpider):
    __spider_name__ = "stock/basic/stock_basic"
    __model__: type[StockBasic] = StockBasic

    def start_requests(self):
        for status in ['L', 'D', 'P']:
            yield self.get_scrapy_request({"list_status": status})


class StockCompanySpider(TushareSpider):
    __spider_name__ = "stock/basic/stock_company"
    __model__: type[StockCompany] = StockCompany

    def start_requests(self):
        conn = self.get_db_engine()

        # 构建子查询
        subquery = select(self.__model__.ts_code)

        # 构建主查询
        query = select(StockBasic.ts_code).where(not_(StockBasic.ts_code.in_(subquery)))

        stock_codes = conn.query_df(query)['ts_code']

        for ts_code in stock_codes:
            yield self.get_scrapy_request({"ts_code": ts_code})


class StkManagersSpider(TushareSpider):
    __spider_name__ = "stock/basic/stk_managers"
    __model__: type[StkManagers] = StkManagers

    def start_requests(self):
        conn = self.get_db_engine()

        # 构建子查询
        subquery = select(self.__model__.ts_code)

        # 构建主查询
        query = select(StockBasic.ts_code).where(not_(StockBasic.ts_code.in_(subquery)))

        stock_codes = conn.query_df(query)['ts_code']

        for ts_code in stock_codes:
            yield self.get_scrapy_request({"ts_code": ts_code})


class StkRewardsSpider(TushareSpider):
    __spider_name__ = "stock/basic/stk_rewards"
    __model__: type[StkRewards] = StkRewards

    def start_requests(self):
        conn = self.get_db_engine()

        # 构建子查询
        subquery = select(self.__model__.ts_code)

        # 构建主查询
        query = select(StockBasic.ts_code).where(not_(StockBasic.ts_code.in_(subquery)))

        stock_codes = conn.query_df(query)['ts_code']

        for ts_code in stock_codes:
            yield self.get_scrapy_request({"ts_code": ts_code})


class NameChangeSpider(TushareSpider):
    __spider_name__ = "stock/basic/namechange"
    __model__: type[Namechange] = Namechange

    def start_requests(self):
        conn = self.get_db_engine()

        # 构建子查询
        subquery = select(self.__model__.ts_code)

        # 构建主查询
        query = select(StockBasic.ts_code).where(not_(StockBasic.ts_code.in_(subquery)))

        stock_codes = conn.query_df(query)['ts_code']

        for ts_code in stock_codes:
            yield self.get_scrapy_request({"ts_code": ts_code})


class HSConstSpider(TushareSpider):
    __spider_name__ = "stock/basic/hs_const"
    __model__: type[HsConst] = HsConst

    def start_requests(self):
        for hs_type in ['SH', 'SZ']:
            yield self.get_scrapy_request({"hs_type": hs_type})


class TradeCalSpider(TushareSpider):
    __spider_name__ = "stock/basic/trade_cal"
    __model__: type[TradeCal] = TradeCal

    def start_requests(self):
        for exchange in ['SSE', 'SZSE']:
            yield self.get_scrapy_request({"exchange": exchange})
