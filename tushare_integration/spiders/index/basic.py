from tushare_integration.spiders.tushare import TushareSpider


class IndexBasicSpider(TushareSpider):
    name = "index/basic/index_basic"

    def start_requests(self):
        markets = ["MSCI", "CSI", "SSE", "SZSE", "CICC", "SW", "OTH"]

        for market in markets:
            params = {"market": market}
            yield self.get_scrapy_request(params)
