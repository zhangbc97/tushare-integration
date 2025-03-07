import datetime

from tushare_models.bak_basic import BakBasic
from tushare_models.hs_const import HsConst
from tushare_models.namechange import Namechange
from tushare_models.new_share import NewShare
from tushare_models.stk_managers import StkManagers
from tushare_models.stk_premarket import StkPremarket
from tushare_models.stk_rewards import StkRewards
from tushare_models.stock_basic import StockBasic
from tushare_models.stock_company import StockCompany
from tushare_models.trade_cal import TradeCal

from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TSCodeSpider, TushareSpider


class StockBasicSpider(TushareSpider):
    __model__: type[StockBasic] = StockBasic

    def start_requests(self):
        for status in ['L', 'D', 'P']:
            yield self.get_httpx_request({"list_status": status})


class StkPremarketSpider(TimeSeriesSpider):
    __model__: type[StkPremarket] = StkPremarket


class TradeCalSpider(TushareSpider):
    __model__: type[TradeCal] = TradeCal

    def start_requests(self):
        for exchange in ["SSE", "SZSE", "CFFEX", "DCE", "CZCE", "SHFE", "INE"]:
            params = {"exchange": exchange}
            yield self.get_httpx_request(params)


class NameChangeSpider(LimitOffsetSpider):
    __model__: type[Namechange] = Namechange
    __limit__: int = 5000


class HSConstSpider(TushareSpider):
    __model__: type[HsConst] = HsConst

    def start_requests(self):
        for hs_type in ['SH', 'SZ']:
            yield self.get_httpx_request({"hs_type": hs_type})


class StockCompanySpider(TushareSpider):
    __model__: type[StockCompany] = StockCompany

    def start_requests(self):
        # 单次数量限制4500，所以需要分批请求
        for exchange in ["SSE", "SZSE"]:
            params = {"exchange": exchange}
            yield self.get_httpx_request(params)


class StkManagersSpider(TSCodeSpider):
    __model__: type[StkManagers] = StkManagers


class StkRewardsSpider(TSCodeSpider):
    __model__: type[StkRewards] = StkRewards


class NewShareSpider(LimitOffsetSpider):
    __model__: type[NewShare] = NewShare

    # 从1990开始一次获取5年，使用start_date和end_date筛选
    def start_requests(self):
        for year in range(1990, datetime.datetime.now().year, 5):
            params = {"start_date": f"{year}0101", "end_date": f"{year+5}0101"}
            yield self.get_httpx_request(params)


class BakBasicSpider(TimeSeriesSpider):
    __model__: type[BakBasic] = BakBasic
