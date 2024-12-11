import logging
from urllib import request
from venv import logger
import pandas as pd
from sqlalchemy import select, distinct

from tushare_integration.spiders.tushare import DailySpider, TushareSpider
from tushare_integration.items import TushareIntegrationItem
from tushare_integration.models.index_classify import IndexClassify
from tushare_integration.models.index_member import IndexMember
from tushare_integration.models.index_member_all import IndexMemberAll
from tushare_integration.models.sw_daily import SwDaily


class IndexClassifySpider(TushareSpider):
    name = "index/sw/index_classify"
    __model__: type[IndexClassify] = IndexClassify


class IndexMemberSpider(TushareSpider):
    name = "index/sw/index_member"
    __model__: type[IndexMember] = IndexMember

    def start_requests(self):
        # 使用 SQLAlchemy select 获取所有的 index_code
        query = select(distinct(IndexClassify.index_code))
        df = self.get_db_engine().query_df(query)

        for index_code in df["index_code"]:
            yield self.get_scrapy_request(
                params={
                    'index_code': index_code,
                }
            )


class IndexMemberAllSpider(TushareSpider):
    name = "index/sw/index_member_all"
    __model__: type[IndexMemberAll] = IndexMemberAll

    def start_requests(self):
        # 通过LIMIT+OFFSET的方取数据
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
    __model__: type[SwDaily] = SwDaily

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 index_code
        query = select(distinct(IndexClassify.index_code))
        df = conn.query_df(query)

        if df.empty:
            return

        for index_code in df['index_code']:
            yield self.get_scrapy_request(params={"index_code": index_code})
