import datetime

from sqlalchemy import and_, distinct, not_, select
from sqlalchemy.sql import func

from tushare_integration.models.fut_daily import FutDaily
from tushare_integration.models.fut_holding import FutHolding
from tushare_integration.models.fut_mapping import FutMapping
from tushare_integration.models.fut_settle import FutSettle
from tushare_integration.models.fut_weekly_detail import FutWeeklyDetail
from tushare_integration.models.fut_wsr import FutWsr
from tushare_integration.models.trade_cal import TradeCal
from tushare_integration.spiders.tushare import TimeSeriesSpider


class FutDailySpider(TimeSeriesSpider):
    __model__: type[FutDaily] = FutDaily

    def start_requests(self):
        conn = self.get_db_engine()
        min_cal_dates = {
            'CFFEX': '20100416',  # 中金所
            'SHFE': '19950417',  # 上期所
            'DCE': '19930705',  # 大商所
            'CZCE': '19910101',  # 郑商所
            'INE': '20180326',  # 上海国际能源交易中心
            'GFEX': '20210419',  # 广期所
        }

        for exchange in min_cal_dates.keys():
            # 构建子查询：获取已有的交易日期
            subquery = select(FutDaily.trade_date).distinct()

            # 构建主查询：获取需要的交易日期
            query = (
                select(distinct(TradeCal.cal_date))
                .where(
                    and_(
                        not_(TradeCal.cal_date.in_(subquery)),
                        TradeCal.is_open == 1,
                        TradeCal.cal_date >= min_cal_dates[exchange],
                        TradeCal.cal_date <= func.today(),
                        TradeCal.exchange == exchange,
                    )
                )
                .order_by(TradeCal.cal_date)
            )

            trade_dates = [d.strftime('%Y%m%d') for d in conn.query_df(query)['cal_date']]

            for trade_date in trade_dates:
                yield self.get_httpx_request(params={"trade_date": trade_date, "exchange": exchange})


class FutHoldingSpider(TimeSeriesSpider):
    """
    期货持仓量
    这个接口的数据量较大，为了保证一致性，针对每个交易所单独按日获取
    """

    __model__: type[FutHolding] = FutHolding

    def start_requests(self):
        conn = self.get_db_engine()
        # 写死每个交易所最早有数据的交易日
        min_cal_dates = {
            'CFFEX': '2010-04-16',  # TODO 这里有个问题，交易日历里面CFFEX最早日期是2015年，直接用日期取数据会更早一些
            'DCE': '2006-01-04',
            'CZCE': '2005-04-29',
            'SHFE': '2002-01-07',
            # 'INE': '2002-01-01', 暂时没获取到INE的数据，先注释掉
        }

        for exchange in min_cal_dates.keys():
            # 构建子查询：获取已有的交易日期
            subquery = select(FutHolding.trade_date).where(FutHolding.exchange == exchange)

            # 构建主查询：获取需要的交易日期
            query = (
                select(distinct(TradeCal.cal_date))
                .where(
                    and_(
                        not_(TradeCal.cal_date.in_(subquery)),
                        TradeCal.is_open == 1,
                        TradeCal.cal_date >= min_cal_dates[exchange],
                        TradeCal.cal_date <= func.today(),
                        TradeCal.exchange == exchange,
                    )
                )
                .order_by(TradeCal.cal_date)
            )

            trade_dates = [d.strftime('%Y%m%d') for d in conn.query_df(query)['cal_date']]

            for trade_date in trade_dates:
                yield self.get_httpx_request(params={"trade_date": trade_date, "exchange": exchange})


class FutSettleSpider(TimeSeriesSpider):
    __model__: type[FutSettle] = FutSettle


class FutMappingSpider(TimeSeriesSpider):
    __model__: type[FutMapping] = FutMapping


class FutWSRSpider(TimeSeriesSpider):
    __model__: type[FutWsr] = FutWsr


class FutWeeklyDetailSpider(TimeSeriesSpider):
    __model__: type[FutWeeklyDetail] = FutWeeklyDetail

    def start_requests(self):
        conn = self.get_db_engine()
        # 使用SQLAlchemy select构建查询
        query = select(distinct(FutWeeklyDetail.week)).order_by(FutWeeklyDetail.week.desc())
        df = conn.query_df(query)

        # 生成历史所有的周编号,从201010开始
        weeks = [str(y) + str(w).zfill(2) for y in range(2010, datetime.datetime.now().year + 1) for w in range(1, 53)]
        # 去掉已经采集的周编号
        weeks = list(set(weeks) - set(df['week'].tolist()))
        # 生成请求
        for week in weeks:
            yield self.get_httpx_request(params={"week": week})
