from tushare_integration.models.fut_basic import FutBasic
from tushare_integration.spiders.tushare import TushareSpider


class FutBasicSpider(TushareSpider):
    __spider_name__ = "future/basic/fut_basic"
    __model__: type[FutBasic] = FutBasic

    def start_requests(self):
        for exchange in ["CFFEX", "DCE", "CZCE", "SHFE", "INE", "GFEX"]:
            params = {"exchange": exchange}
            yield self.get_scrapy_request(params)
