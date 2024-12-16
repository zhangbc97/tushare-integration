import pandas as pd
from sqlalchemy import not_, select

from tushare_integration.items import TushareIntegrationItem
from tushare_integration.models.hs_const import HsConst
from tushare_integration.models.namechange import Namechange
from tushare_integration.models.stk_managers import StkManagers
from tushare_integration.models.stk_rewards import StkRewards
from tushare_integration.models.stock_basic import StockBasic
from tushare_integration.models.stock_company import StockCompany
from tushare_integration.models.trade_cal import TradeCal
from tushare_integration.spiders.tushare import TushareSpider


class StockBasicSpider(TushareSpider):
    __model__: type[StockBasic] = StockBasic

    def start_requests(self):
        for status in ['L', 'D', 'P']:
            yield self.get_scrapy_request({"list_status": status})


class StockCompanySpider(TushareSpider):
    __model__: type[StockCompany] = StockCompany

    def start_requests(self):
        for exchange in ["SSE", "SZSE"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)


class StkManagersSpider(TushareSpider):
    __model__: type[StkManagers] = StkManagers


class StkRewardsSpider(TushareSpider):
    __model__: type[StkRewards] = StkRewards


class NameChangeSpider(TushareSpider):
    __model__: type[Namechange] = Namechange

    def start_requests(self):
        # 不能用start_date和end_date筛选，部分数据没有ann_date导致无法完整同步数据
        # 每次拉5000条数据
        request = self.get_scrapy_request(params={'offset': 0, 'limit': 5000})
        request.meta["offset"] = 0
        request.meta["limit"] = 5000
        yield request

    def parse(self, response, **kwargs):
        first_page = self.parse_response(response, **kwargs)
        if first_page["data"].empty:
            return None

        all_data = [first_page["data"]]
        offset = response.meta["offset"] + response.meta["limit"]
        limit = response.meta["limit"]

        while True:
            parsed_data = self.request_with_requests(params={'offset': offset, 'limit': limit})
            if parsed_data["data"].empty:
                break
            all_data.append(parsed_data["data"])
            offset += limit

        return TushareIntegrationItem(data=pd.concat(all_data, ignore_index=True))


class HSConstSpider(TushareSpider):
    __model__: type[HsConst] = HsConst

    def start_requests(self):
        for hs_type in ['SH', 'SZ']:
            yield self.get_scrapy_request({"hs_type": hs_type})


class TradeCalSpider(TushareSpider):
    __model__: type[TradeCal] = TradeCal

    def start_requests(self):
        for exchange in ["SSE", "SZSE", "CFFEX", "DCE", "CZCE", "SHFE", "INE"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)
