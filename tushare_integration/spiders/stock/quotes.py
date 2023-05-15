import pandas as pd
from sqlalchemy import text

from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class StockDailySpider(DailySpider):
    name = "stock/quotes/daily"
    custom_settings = {"TABLE_NAME": "daily"}


class StockWeeklySpider(TushareSpider):
    name = "stock/quotes/weekly"
    custom_settings = {"TABLE_NAME": "weekly"}

    def start_requests(self):
        conn = self.get_db_conn()
        db_name = self.settings.get("DB_NAME")
        table_name = self.get_table_name()

        trade_dates = pd.DataFrame([
            cal_date[0]
            for cal_date in conn.execute(
                text(f"""
                SELECT DISTINCT cal_date
                FROM {db_name}.trade_cal
                WHERE is_open = 1
                  AND cal_date <= today()
                  AND exchange = 'SSE'
                ORDER BY cal_date
                """)  # 期货交易日历共享同一张表，所以这里过滤SSE
            ).fetchall()
        ], columns=['cal_date'])

        trade_dates['cal_date'] = pd.to_datetime(trade_dates['cal_date'])
        trade_dates = trade_dates.assign(trade_date_index=lambda x: x['cal_date'].astype('datetime64[ns]')).set_index(
            'trade_date_index').resample('W').agg({'cal_date': 'last'}).reset_index(drop=True)
        # 找出weekly中所有交易日，判断没在trade_dates中的，就是需要更新的
        weekly_trade_dates = pd.DataFrame([
            cal_date[0]
            for cal_date in conn.execute(
                text(f"""
                SELECT DISTINCT trade_date
                FROM {db_name}.{table_name}
                ORDER BY trade_date
                """)
            ).fetchall()
        ], columns=['trade_date'])

        weekly_trade_dates['trade_date'] = pd.to_datetime(weekly_trade_dates['trade_date'])
        trade_dates = trade_dates[~trade_dates['cal_date'].isin(weekly_trade_dates['trade_date'])]

        for trade_date in trade_dates['cal_date']:
            yield self.get_scrapy_request(
                params={"trade_date": trade_date.strftime("%Y%m%d")}
            )


class StockMonthlySpider(TushareSpider):
    name = "stock/quotes/monthly"
    custom_settings = {"TABLE_NAME": "monthly"}

    def start_requests(self):
        conn = self.get_db_conn()
        db_name = self.settings.get("DB_NAME")
        table_name = self.get_table_name()

        trade_dates = pd.DataFrame([
            cal_date[0]
            for cal_date in conn.execute(
                text(f"""
                SELECT DISTINCT cal_date
                FROM {db_name}.trade_cal
                WHERE is_open = 1
                  AND cal_date <= today()
                  AND exchange = 'SSE'
                ORDER BY cal_date
                """)  # 期货交易日历共享同一张表，所以这里过滤SSE
            ).fetchall()
        ], columns=['cal_date'])

        trade_dates['cal_date'] = pd.to_datetime(trade_dates['cal_date'])
        trade_dates = trade_dates.assign(trade_date_index=lambda x: x['cal_date'].astype('datetime64[ns]')).set_index(
            'trade_date_index').resample('M').agg({'cal_date': 'last'}).reset_index(drop=True)
        # 找出weekly中所有交易日，判断没在trade_dates中的，就是需要更新的
        weekly_trade_dates = pd.DataFrame([
            cal_date[0]
            for cal_date in conn.execute(
                text(f"""
                SELECT DISTINCT trade_date
                FROM {db_name}.{table_name}
                ORDER BY trade_date
                """)
            ).fetchall()
        ], columns=['trade_date'])

        weekly_trade_dates['trade_date'] = pd.to_datetime(weekly_trade_dates['trade_date'])
        trade_dates = trade_dates[~trade_dates['cal_date'].isin(weekly_trade_dates['trade_date'])]

        for trade_date in trade_dates['cal_date']:
            yield self.get_scrapy_request(
                params={"trade_date": trade_date.strftime("%Y%m%d")}
            )


class AdjFactorSpider(DailySpider):
    name = "stock/quotes/adj_factor"
    custom_settings = {"TABLE_NAME": "adj_factor"}


class SuspendDSpider(DailySpider):
    name = "stock/quotes/suspend_d"
    custom_settings = {"TABLE_NAME": "suspend_d"}


class HSGTTop10Spider(DailySpider):
    name = "stock/quotes/hsgt_top10"
    custom_settings = {"TABLE_NAME": "hsgt_top10"}


class MoneyFlowSpider(DailySpider):
    name = "stock/quotes/moneyflow"
    custom_settings = {"TABLE_NAME": "moneyflow"}


class MoneyFlowHSGTSpider(DailySpider):
    name = "stock/quotes/moneyflow_hsgt"
    custom_settings = {"TABLE_NAME": "moneyflow_hsgt"}


class StkLimitSpider(DailySpider):
    name = "stock/quotes/stk_limit"
    custom_settings = {"TABLE_NAME": "stk_limit", 'MIN_CAL_DATE': '2007-01-01'}


class DailyBasicSpider(DailySpider):
    name = "stock/quotes/daily_basic"
    custom_settings = {"TABLE_NAME": "daily_basic"}


class GGTTop10Spider(DailySpider):
    name = "stock/quotes/ggt_top10"
    custom_settings = {"TABLE_NAME": "ggt_top10"}


class GGTDailySpider(DailySpider):
    name = "stock/quotes/ggt_daily"
    custom_settings = {"TABLE_NAME": "ggt_daily"}


class BakDailySpider(DailySpider):
    name = "stock/quotes/bak_daily"
    custom_settings = {"TABLE_NAME": "bak_daily"}

# 港股通每月成交统计数据只更新到2020年底，在这里不开发策略