import httpx
import pandas as pd
from sqlalchemy import distinct, select

from tushare_integration.models.index_classify import IndexClassify
from tushare_integration.models.index_member import IndexMember
from tushare_integration.models.index_member_all import IndexMemberAll
from tushare_integration.models.sw_daily import SwDaily
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider


class IndexClassifySpider(TushareSpider):

    __model__: type[IndexClassify] = IndexClassify


class IndexMemberSpider(TushareSpider):

    __model__: type[IndexMember] = IndexMember

    def start_requests(self):
        # 使用 SQLAlchemy select 获取所有的 index_code
        query = select(distinct(IndexClassify.index_code))
        df = self.get_db_engine().query_df(query)

        for index_code in df["index_code"]:
            yield self.get_httpx_request(
                params={
                    'index_code': index_code,
                }
            )


class IndexMemberAllSpider(LimitOffsetSpider):
    __model__: type[IndexMemberAll] = IndexMemberAll
    __limit__: int = 3000


class SWDailySpider(TimeSeriesSpider):
    __model__: type[SwDaily] = SwDaily

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 index_code
        query = select(distinct(IndexClassify.index_code))
        df = conn.query_df(query)

        if df.empty:
            return

        for index_code in df['index_code']:
            yield self.get_httpx_request(params={"index_code": index_code})
