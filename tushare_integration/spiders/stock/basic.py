import datetime

from tushare_integration.spiders.tushare import DailySpider, TSCodeSpider, TushareSpider


class StockBasicSpider(TushareSpider):
    name = "stock/basic/stock_basic"
    description = '股票列表'
    api_name = "stock_basic"

    def start_requests(self):
        exchanges = ["SSE", "SZSE"]
        list_statuses = ["L", "D", "P"]

        for exchange in exchanges:
            for list_status in list_statuses:
                params = {"exchange": exchange, "list_status": list_status}
                yield self.get_scrapy_request(params)


class StockNameChangeSpider(TushareSpider):
    name = "stock/basic/namechange"
    description = '股票名称变更'
    api_name = "namechange"

    def start_requests(self):
        # 不能用start_date和end_date筛选，部分数据没有ann_date导致无法完整同步数据
        # 每次拉5000条数据
        request = self.get_scrapy_request(params={'offset': 0, 'limit': 5000})
        request.meta["offset"] = 0
        request.meta["limit"] = 5000

        yield request

    def parse(self, response, **kwargs):
        parsed_data = self.parse_response(response, **kwargs)
        # data为空时，说明已经拉完所有数据
        if parsed_data["data"].empty:
            return
        yield parsed_data
        # 继续拉取下一页数据
        request = self.get_scrapy_request(
            params={'offset': response.meta["offset"] + response.meta["limit"], 'limit': response.meta["limit"]}
        )
        request.meta["offset"] = response.meta["offset"] + response.meta["limit"]
        request.meta["limit"] = response.meta["limit"]
        yield request


class StockHSConstSpider(TushareSpider):
    name = "stock/basic/hs_const"
    description = '沪深股通成份股'
    api_name = "hs_const"

    def start_requests(self):
        for hs_type in ["SH", "SZ"]:
            params = {"hs_type": hs_type}
            yield self.get_scrapy_request(params)


class TradeCalSpider(TushareSpider):
    name = "stock/basic/trade_cal"
    api_name = "trade_cal"
    description = '交易日历'
    custom_settings = {"TABLE_NAME": "trade_cal"}

    def start_requests(self):
        for exchange in ["SSE", "SZSE", "CFFEX", "DCE", "CZCE", "SHFE", "INE"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)


class StockCompanySpider(TushareSpider):
    name = "stock/basic/stock_company"
    description = '上市公司基本信息'
    api_name = "stock_company"

    def start_requests(self):
        for exchange in ["SSE", "SZSE"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)


class StockManagers(TSCodeSpider):
    name = "stock/basic/stk_managers"
    description = '上市公司管理层'
    api_name = "stk_managers"


class StockRewards(TSCodeSpider):
    name = "stock/basic/stk_rewards"
    description = '管理层薪酬和持股'
    api_name = "stk_rewards"


class StockNewShareSpider(TushareSpider):
    name = "stock/basic/new_share"
    description = 'IPO新股上市'
    api_name = "new_share"

    def start_requests(self):
        # 用start_date和end_date筛选，每次拉取一年的数据
        for year in range(1990, datetime.datetime.now().year + 1, 5):
            params = {"start_date": str(year) + "0101", "end_date": str(year + 5) + "1231"}
            yield self.get_scrapy_request(params)


class StkPremarket(DailySpider):
    name = "stock/basic/stk_premarket"
    description = '每日股本(盘前数据)'
    api_name = "stk_premarket"


class StockBakBasicSpider(DailySpider):
    name = "stock/basic/bak_basic"
    description = '备用列表'
    api_name = "bak_basic"
    custom_settings = {"MIN_CAL_DATE": "2016-08-01"}
