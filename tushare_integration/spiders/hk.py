import datetime

import httpx
import pandas as pd
from sqlalchemy import and_, func, select

from tushare_integration.models.hk_basic import HkBasic
from tushare_integration.models.hk_daily import HkDaily
from tushare_integration.models.hk_daily_adj import HkDailyAdj
from tushare_integration.models.hk_mins import HkMins
from tushare_integration.models.hk_tradecal import HkTradecal
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider


class HkBasicSpider(TushareSpider):
    __model__: type[HkBasic] = HkBasic


class HkTradecalSpider(LimitOffsetSpider):
    __model__: type[HkTradecal] = HkTradecal


class HkDailySpider(TimeSeriesSpider):
    __model__: type[HkDaily] = HkDaily
    __trade_cal_model__: type[HkTradecal] = HkTradecal

    def start_requests(self):
        # 根据港股交易日历获取每天的交易日期，并格式化为 YYYYMMDD
        for trade_date in self.get_trade_dates("D"):
            if isinstance(trade_date, (datetime.date, datetime.datetime)):
                trade_date_str = trade_date.strftime("%Y%m%d")
            else:
                trade_date_str = trade_date
            yield self.get_httpx_request(params={"trade_date": trade_date_str})


class HkDailyAdjSpider(TimeSeriesSpider):
    __model__: type[HkDailyAdj] = HkDailyAdj

    def start_requests(self):
        # 同样按日通过 get_trade_dates 方法采集复权行情数据
        for trade_date in self.get_trade_dates("D"):
            if isinstance(trade_date, (datetime.date, datetime.datetime)):
                trade_date_str = trade_date.strftime("%Y%m%d")
            else:
                trade_date_str = trade_date
            yield self.get_httpx_request(params={"trade_date": trade_date_str})


class HkMinsSpider(TushareSpider):
    __model__: type[HkMins] = HkMins

    def start_requests(self):
        conn = self.get_db_engine()
        # 从港股基本数据表中获取所有港股代码
        query = select(HkBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            # 查询该代码已采集的分钟数据交易日期，避免重复请求
            exists_date_df = self.get_db_engine().query_df(
                select(func.to_date(self.__model__.trade_time).label('trade_date'))
                .distinct()
                .where(self.__model__.ts_code == ts_code)
            )
            if exists_date_df.empty:
                exists_date = []
            else:
                exists_date = list(exists_date_df['trade_date'].dt.date)

            # 利用港股日线数据来确定需要采集的交易日期
            query_dates = (
                select(HkDaily.trade_date)
                .distinct()
                .where(and_(HkDaily.ts_code == ts_code, HkDaily.trade_date >= self.__model__.__start_date__))
                .order_by(HkDaily.trade_date)
            )
            trade_dates_df = self.get_db_engine().query_df(query_dates)
            if trade_dates_df.empty:
                continue
            trade_dates = list(trade_dates_df['trade_date'].dt.date)
            last_end_date = None
            for trade_date in trade_dates:
                if trade_date in exists_date:
                    continue
                if last_end_date and trade_date <= last_end_date:
                    continue

                # 假定港股交易的分钟数据采集时段为当天09:00到16:00
                start_dt = datetime.datetime.combine(trade_date, datetime.time(9, 0, 0))
                end_dt = datetime.datetime.combine(trade_date, datetime.time(16, 0, 0))
                yield self.get_httpx_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_date": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
                        "freq": "1min",
                    },
                    extensions={'exists_date': exists_date},
                )
                last_end_date = trade_date  # 更新最后采集的交易日期

    def parse(self, response: httpx.Response, **kwargs):
        exists_date = response.request.extensions.get('exists_date', [])
        data: pd.DataFrame = self.parse_response(response)
        if data.empty or len(data) == 0:
            return
        # 确保 trade_time 字段转换为 datetime 类型
        data['trade_time'] = data['trade_time'].astype(str)
        data['trade_time'] = pd.to_datetime(data['trade_time'])
        pipe_item = pd.DataFrame()
        for trade_date, group in data.groupby(data['trade_time'].dt.date):
            if trade_date in exists_date:
                continue
            pipe_item = pd.concat([pipe_item, group])
        yield pipe_item
