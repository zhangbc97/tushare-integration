from tushare_integration.spiders.tushare import DailySpider, TushareSpider
from tushare_integration.models.index_basic import IndexBasic
from tushare_integration.models.index_daily import IndexDaily
from tushare_integration.models.index_weight import IndexWeight
from tushare_integration.models.index_dailybasic import IndexDailybasic
from tushare_integration.models.index_classify import IndexClassify
from tushare_integration.models.index_member import IndexMember
from sqlalchemy import select, and_


class IndexBasicSpider(TushareSpider):
    name = "stock/index/index_basic"
    __model__: type[IndexBasic] = IndexBasic

    def start_requests(self):
        for market in ['MSCI', 'CSI', 'SSE', 'SZSE', 'CICC', 'SW', 'OTH']:
            yield self.get_scrapy_request({"market": market})


class IndexDailySpider(DailySpider):
    name = "stock/index/index_daily"
    __model__: type[IndexDaily] = IndexDaily


class IndexWeightSpider(TushareSpider):
    name = "stock/index/index_weight"
    __model__: type[IndexWeight] = IndexWeight

    def start_requests(self):
        conn = self.get_db_engine()

        # 获取所有指数代码
        stmt = select(IndexBasic.ts_code).where(IndexBasic.market.in_(['MSCI', 'CSI', 'SSE', 'SZSE']))
        index_codes = conn.query_df(stmt)['ts_code']

        # 获取所有交易日期
        model = self.__model__
        stmt = (
            select(IndexDaily.trade_date)
            .distinct()
            .where(
                and_(
                    IndexDaily.ts_code.in_(
                        select(IndexBasic.ts_code).where(IndexBasic.market.in_(['MSCI', 'CSI', 'SSE', 'SZSE']))
                    ),
                    IndexDaily.trade_date >= self.start_date,
                    ~IndexDaily.trade_date.in_(select(model.__table__.c.trade_date).distinct()),
                )
            )
        )
        trade_dates = conn.query_df(stmt)['trade_date']

        for trade_date in trade_dates.dt.date:
            for ts_code in index_codes:
                yield self.get_scrapy_request({"index_code": ts_code, "trade_date": trade_date.strftime("%Y%m%d")})


class IndexDailyBasicSpider(DailySpider):
    name = "stock/index/index_dailybasic"
    __model__: type[IndexDailybasic] = IndexDailybasic


class IndexClassifySpider(TushareSpider):
    name = "stock/index/index_classify"
    __model__: type[IndexClassify] = IndexClassify

    def start_requests(self):
        for level in ['L1', 'L2', 'L3']:
            for src in ['SW2021', 'SW2014', 'SW']:
                yield self.get_scrapy_request({"level": level, "src": src})


class IndexMemberSpider(TushareSpider):
    name = "stock/index/index_member"
    __model__: type[IndexMember] = IndexMember

    def start_requests(self):
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有指数代码
        query = select(IndexClassify.index_code)
        index_codes = conn.query_df(query)['index_code']

        for index_code in index_codes:
            yield self.get_scrapy_request({"index_code": index_code})
