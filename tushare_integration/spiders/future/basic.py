from tushare_integration.spiders.tushare import TushareSpider


class FutBasicSpider(TushareSpider):
    name = "future/basic/fut_basic"
    custom_settings = {"TABLE_NAME": "fut_basic"}

    def start_requests(self):
        for exchange in ["CFFEX", "DCE", "CZCE", "SHFE", "INE", "GFEX"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)
