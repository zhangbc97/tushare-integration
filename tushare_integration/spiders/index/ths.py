from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class THSDailySpider(DailySpider):
    name = "index/ths/ths_daily"
    custom_settings = {"TABLE_NAME": "ths_daily"}


class THSIndexSpider(TushareSpider):
    name = "index/ths/ths_index"
    custom_settings = {"TABLE_NAME": "ths_index"}


class THSMember(TushareSpider):
    name = "index/ths/ths_member"
    custom_settings = {"TABLE_NAME": "ths_member"}

    def start_requests(self):
        # 从index_classify表中获取所有的index_code，然后构造请求
        df = self.get_db_engine().query_df("select distinct ts_code from ths_index")

        for ts_code in df["ts_code"]:
            yield self.get_scrapy_request(
                params={
                    'ts_code': ts_code,
                }
            )
