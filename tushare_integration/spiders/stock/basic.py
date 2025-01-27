import httpx
import pandas as pd

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
            yield self.get_httpx_request({"list_status": status})


class StockCompanySpider(TushareSpider):
    __model__: type[StockCompany] = StockCompany

    def start_requests(self):
        for exchange in ["SSE", "SZSE"]:
            params = {"exchange": exchange}
            yield self.get_httpx_request(params)


class StkManagersSpider(TushareSpider):
    __model__: type[StkManagers] = StkManagers


class StkRewardsSpider(TushareSpider):
    __model__: type[StkRewards] = StkRewards


class NameChangeSpider(TushareSpider):
    __model__: type[Namechange] = Namechange

    def start_requests(self):
        # 不能用start_date和end_date筛选，部分数据没有ann_date导致无法完整同步数据
        # 每次拉5000条数据
        request = self.get_httpx_request(params={'offset': 0, 'limit': 5000})
        request.extensions["offset"] = 0
        request.extensions["limit"] = 5000
        yield request

    def parse(self, response: httpx.Response, **kwargs):
        first_page = self.parse_response(response, **kwargs)
        if first_page.empty:
            return None

        all_data = [first_page]
        offset = response.request.extensions["offset"] + response.request.extensions["limit"]
        limit = response.request.extensions["limit"]

        while True:
            parsed_data = self.parse_response(
                self._process_request(self.get_httpx_request(params={'offset': offset, 'limit': limit}))
            )
            if parsed_data.empty:
                break
            all_data.append(parsed_data)
            offset += limit

        return pd.concat(all_data, ignore_index=True)


class HSConstSpider(TushareSpider):
    __model__: type[HsConst] = HsConst

    def start_requests(self):
        for hs_type in ['SH', 'SZ']:
            yield self.get_httpx_request({"hs_type": hs_type})


class TradeCalSpider(TushareSpider):
    __model__: type[TradeCal] = TradeCal

    def start_requests(self):
        for exchange in ["SSE", "SZSE", "CFFEX", "DCE", "CZCE", "SHFE", "INE"]:
            params = {"exchange": exchange}
            yield self.get_httpx_request(params)
