from tushare_integration.spiders.tushare import TushareSpider


class IndexClassifySpider(TushareSpider):
    name = "index/sw/index_classify"
    custom_settings = {"TABLE_NAME": "index_classify"}


class IndexMemberSpider(TushareSpider):
    name = "index/sw/index_member"
    custom_settings = {"TABLE_NAME": "index_member"}

    def start_requests(self):
        # 从index_classify表中获取所有的index_code，然后构造请求
        df = self.get_db_engine().query_df("select distinct index_code from index_classify")

        for index_code in df["index_code"]:
            yield self.get_scrapy_request(
                params={
                    'index_code': index_code,
                }
            )
