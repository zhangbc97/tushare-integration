import calendar
import datetime
import logging
from typing import Any

import pandas as pd

from tushare_integration.items import TushareIntegrationItem
from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class StockDailySpider(DailySpider):
    name = "stock/quotes/daily"
    custom_settings = {"TABLE_NAME": "daily"}


class StockWeeklySpider(TushareSpider):
    name = "stock/quotes/weekly"
    custom_settings = {"TABLE_NAME": "weekly"}

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        table_name = self.get_table_name()

        trade_dates = self.get_trade_dates(conn, db_name, table_name, period='W')

        for trade_date in trade_dates['cal_date']:
            yield self.get_scrapy_request(params={"trade_date": trade_date.strftime("%Y%m%d")})

    def get_trade_dates(self, conn, db_name, table_name, period):
        trade_dates = conn.query_df(
            f"""
                SELECT DISTINCT cal_date
                FROM {db_name}.trade_cal
                WHERE is_open = 1
                    AND cal_date <= today()
                    AND exchange = 'SSE'
                ORDER BY cal_date
                """
        )

        trade_dates['cal_date'] = pd.to_datetime(trade_dates['cal_date'])
        trade_dates = (
            trade_dates.assign(trade_date_index=lambda x: x['cal_date'].astype('datetime64[ns]'))
            .set_index('trade_date_index')
            .resample(period)
            .agg({'cal_date': 'last'})
            .reset_index(drop=True)
            .dropna()
        )

        # 找出weekly中所有交易日，判断没在trade_dates中的，就是需要更新的
        period_trade_dates = conn.query_df(
            f"""
                SELECT DISTINCT trade_date
                FROM {db_name}.{table_name}
                ORDER BY trade_date
                """
        )

        if period_trade_dates.empty:
            period_trade_dates = pd.DataFrame(columns=['trade_date'])
        else:
            period_trade_dates['trade_date'] = pd.to_datetime(period_trade_dates['trade_date'])
        trade_dates = trade_dates[~trade_dates['cal_date'].isin(period_trade_dates['trade_date'])]
        return trade_dates


class StockMonthlySpider(StockWeeklySpider):
    name = "stock/quotes/monthly"
    custom_settings = {"TABLE_NAME": "monthly"}

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        table_name = self.get_table_name()

        trade_dates = self.get_trade_dates(conn, db_name, table_name, period='ME')

        for trade_date in trade_dates['cal_date']:
            yield self.get_scrapy_request(params={"trade_date": trade_date.strftime("%Y%m%d")})


class StockWeeklyMonthlySpider(StockWeeklySpider):
    name = "stock/quotes/stk_weekly_monthly"
    custom_settings = {"TABLE_NAME": "stk_weekly_monthly"}

    def get_latest_trade_date(self, conn, db_name, date):
        trade_dates = conn.query_df(
            f"""
                SELECT max(cal_date) AS `trade_date`
                FROM {db_name}.trade_cal
                WHERE is_open = 1
                    AND cal_date <= '{date}'
                    AND exchange = 'SSE'
                """
        )

        if trade_dates.empty:
            return date

        return trade_dates['trade_date'].iloc[-1]

    def get_weekly_trade_date(self):
        today = datetime.date.today()
        weekday = today.weekday()
        if weekday == 6:
            return today
        sunday = (today + datetime.timedelta(days=6 - weekday)).strftime("%Y-%m-%d")

        return self.get_latest_trade_date(self.get_db_engine(), self.spider_settings.database.db_name, sunday)

    def get_end_of_month(self):
        today = datetime.date.today()
        end_date_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1]).strftime("%Y-%m-%d")

        return self.get_latest_trade_date(
            self.get_db_engine(), self.spider_settings.database.db_name, end_date_of_month
        )

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        table_name = self.get_table_name()

        weekly_trade_dates = self.get_trade_dates(conn, db_name, table_name, period='W')
        weekly_trade_dates = pd.concat(
            [weekly_trade_dates, pd.DataFrame([{'cal_date': self.get_weekly_trade_date()}])], ignore_index=True
        )
        weekly_trade_dates['freq'] = 'week'

        monthly_trade_dates = self.get_trade_dates(conn, db_name, table_name, period='ME')
        monthly_trade_dates = pd.concat(
            [monthly_trade_dates, pd.DataFrame([{'cal_date': self.get_end_of_month()}])], ignore_index=True
        )
        monthly_trade_dates['freq'] = 'month'

        trade_dates = pd.concat([weekly_trade_dates, monthly_trade_dates], ignore_index=True)

        for trade_date, freq in trade_dates[['cal_date', 'freq']].itertuples(index=False):
            yield self.get_scrapy_request(params={"trade_date": trade_date.strftime("%Y%m%d"), "freq": freq})


class AdjFactorSpider(DailySpider):
    name = "stock/quotes/adj_factor"
    custom_settings = {"TABLE_NAME": "adj_factor"}


class SuspendDSpider(DailySpider):
    name = "stock/quotes/suspend_d"
    custom_settings = {"TABLE_NAME": "suspend_d", 'MIN_CAL_DATE': '1999-05-04'}


class HSGTTop10Spider(DailySpider):
    name = "stock/quotes/hsgt_top10"
    custom_settings = {"TABLE_NAME": "hsgt_top10", "MIN_CAL_DATE": "2014-11-17"}


class StkLimitSpider(DailySpider):
    name = "stock/quotes/stk_limit"
    custom_settings = {"TABLE_NAME": "stk_limit", 'MIN_CAL_DATE': '2007-01-01'}


class DailyBasicSpider(DailySpider):
    name = "stock/quotes/daily_basic"
    custom_settings = {"TABLE_NAME": "daily_basic"}


class GGTTop10Spider(DailySpider):
    name = "stock/quotes/ggt_top10"
    custom_settings = {"TABLE_NAME": "ggt_top10", "MIN_CAL_DATE": "2014-11-17"}


class GGTDailySpider(DailySpider):
    name = "stock/quotes/ggt_daily"
    custom_settings = {"TABLE_NAME": "ggt_daily", "MIN_CAL_DATE": "2014-11-17"}


class BakDailySpider(DailySpider):
    name = "stock/quotes/bak_daily"
    custom_settings = {"TABLE_NAME": "bak_daily", 'MIN_CAL_DATE': '2017-06-14'}


# 港股通每月成交统计数据只更新到2020年底，在这里不开发策略


# noinspection SqlNoDataSourceInspection
class StockMin(TushareSpider):
    name = "stock/quotes/stk_mins"
    custom_settings: dict[str, Any] = {
        "TABLE_NAME": "stk_mins",
        "BASIC_TABLE": "stock_basic",
        "DAILY_TABLE": "daily",
        "MIN_CAL_DATE": "2009-01-01",
    }

    # noinspection SqlDialectInspection
    def start_requests(self):
        # 取所有的ts_code,按日筛分钟线
        for ts_code in self.get_db_engine().query_df(
            f""" SELECT ts_code FROM {self.spider_settings.database.db_name}.{self.custom_settings.get("BASIC_TABLE")}"""
        )['ts_code']:
            # 不同的数据库查询语句不同，这里可能需要特殊定制
            # 主要差异在toDate函数上，支持了自定义函数，放到DBEngine中
            exists_date_df = self.get_db_engine().query_df(
                f"""
                    SELECT DISTINCT {self.get_db_engine().functions.get('to_date', 'to_date')}(trade_time) AS `trade_date`
                    FROM {self.spider_settings.database.db_name}.{self.get_table_name()}
                    WHERE ts_code = '{ts_code}'"""
            )
            if exists_date_df.empty:
                exists_date = []
            else:
                exists_date = list(exists_date_df['trade_date'].dt.date)
            trade_dates = self.get_db_engine().query_df(
                f"""
                    SELECT DISTINCT trade_date 
                    FROM {self.spider_settings.database.db_name}.{self.custom_settings.get("DAILY_TABLE")}
                    WHERE ts_code = '{ts_code}' AND trade_date >= '{self.custom_settings.get("MIN_CAL_DATE")}'
                    ORDER BY trade_date"""
            )
            if trade_dates.empty:
                continue
            trade_dates = list(trade_dates['trade_date'].dt.date)
            # logging.error(f"ts_code: {ts_code[0]}, exists_date: {exists_date}, trade_dates: {trade_dates}")
            # 当我们看到一个交易日的时候，直接拉取这个交易日和后面40天的数据
            # 大表的REPLACE INTO性能极差，不能使用REPLACE INTO的方案
            last_end_date = None
            for trade_date in trade_dates:
                # 如果这个交易日已经存在，那么就不需要再拉取了
                if trade_date in exists_date:
                    continue
                # 如果有last_end_date，那么就是在上一次请求的基础上继续拉取
                # 如果trade_date在last_end_date之前，那么就不需要再拉取了
                if last_end_date and trade_date <= last_end_date:
                    continue

                # 符合条件直接拉取接下来40天的数据
                yield self.get_scrapy_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": trade_date.strftime("%Y-%m-%d") + " 09:00:00",
                        "end_date": (trade_date + datetime.timedelta(days=40)).strftime("%Y-%m-%d") + " 16:00:00",
                        "freq": "1min",
                    },
                    meta={
                        'exists_date': exists_date,
                    },
                )
                # 把last_end_date更新为当前trade_date + 40天
                last_end_date = trade_date + datetime.timedelta(days=40)

    def parse(self, response, **kwargs):
        exists_date = response.meta['exists_date']
        item = self.parse_response(response)
        # 一次采集多天的数据，需要逐天判断长度是否是241，如果是则写入数据库，否则报日志并且丢弃
        # start_requests中已经保证单个任务中不会重复采集，判断当前的交易日是否在exists_date中即可，不需要关心是否在本次采集中重复采集
        data: pd.DataFrame = item['data']

        if len(data) == 0:
            return

        data['trade_time'] = pd.to_datetime(data['trade_time'])

        pipe_item = pd.DataFrame()

        for trade_date, values in data.groupby(data['trade_time'].dt.date):
            # 在exists_date中的交易日不需要再次写入，说明在本地采集开始前就已经有数据了
            # 单个采集任务中不会重复采集，所以不需要判断是否在本次采集中重复采集
            if trade_date in exists_date:
                continue
            # 如果不在exists_date中，那么就需要判断长度是否是241，如果不是241，那么就报错并且丢弃
            if len(values) != 241:
                logging.error(f"length of data is not 241, params: {response.meta['params']}")
                continue

            pipe_item = pd.concat([pipe_item, values])
        # 减少写入次数
        yield TushareIntegrationItem(data=pipe_item)
