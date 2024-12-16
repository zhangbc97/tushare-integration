from tushare_integration.models.index_basic import IndexBasic
from tushare_integration.spiders.tushare import TushareSpider


class IndexBasicSpider(TushareSpider):
    __model__: type[IndexBasic] = IndexBasic

    def start_requests(self):
        markets = ["MSCI", "CSI", "SSE", "SZSE", "CICC", "SW", "OTH"]

        for market in markets:
            params = {"market": market}
            yield self.get_scrapy_request(params)
