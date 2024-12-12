from sqlalchemy import distinct, select

from tushare_integration.models.ths_daily import ThsDaily
from tushare_integration.models.ths_index import ThsIndex
from tushare_integration.models.ths_member import ThsMember
from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class THSDailySpider(DailySpider):
    __spider_name__ = "index/ths/ths_daily"
    __model__: type[ThsDaily] = ThsDaily

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 ts_code
        query = select(distinct(ThsIndex.ts_code))
        df = conn.query_df(query)

        if df.empty:
            return

        for ts_code in df['ts_code']:
            yield self.get_scrapy_request(params={"ts_code": ts_code})


class THSIndexSpider(TushareSpider):
    __spider_name__ = "index/ths/ths_index"
    __model__: type[ThsIndex] = ThsIndex


class THSMember(TushareSpider):
    __spider_name__ = "index/ths/ths_member"
    __model__: type[ThsMember] = ThsMember

    def start_requests(self):
        # 使用 SQLAlchemy select 获取所有的 ts_code
        query = select(distinct(ThsIndex.ts_code))
        df = self.get_db_engine().query_df(query)

        for ts_code in df["ts_code"]:
            yield self.get_scrapy_request(
                params={
                    'ts_code': ts_code,
                }
            )
