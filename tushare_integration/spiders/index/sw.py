import logging
from urllib import request
from venv import logger
import pandas as pd

from tushare_integration.spiders.tushare import DailySpider, TushareSpider
from tushare_integration.items import TushareIntegrationItem


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


class IndexMemberAllSpider(TushareSpider):
    name = "index/sw/index_member_all"
    custom_settings = {"TABLE_NAME": "index_member_all"}

    def start_requests(self):
        # 通过LIMIT+OFFSET的方式取数据
        request = self.get_scrapy_request(params={'offset': 0, 'limit': 3000})
        request.meta["offset"] = 0
        request.meta["limit"] = 3000
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


class SWDailySpider(DailySpider):
    name = "index/sw/sw_daily"
    custom_settings = {"TABLE_NAME": "sw_daily"}
