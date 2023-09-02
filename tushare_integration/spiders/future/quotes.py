from sqlalchemy import create_engine, text

from tushare_integration.spiders.tushare import DailySpider


class FutDailySpider(DailySpider):
    name = "future/quotes/fut_daily"
    custom_settings = {"TABLE_NAME": "fut_daily"}


class FutHoldingSpider(DailySpider):
    """
    期货持仓量
    这个接口的数据量较大，为了保证一致性，针对每个交易所单独按日获取
    """

    name = "future/quotes/fut_holding"
    custom_settings = {"TABLE_NAME": "fut_holding"}

    def start_requests(self):
        conn = self.get_db_engine()
        # 写死每个交易所最早有数据的交易日
        min_cal_dates = {
            'CFFEX': '2010-04-16',
            'DCE': '2006-01-04',
            'CZCE': '2005-04-29',
            'SHFE': '2002-01-07',
            'INE': '2002-01-01',
        }

        for exchange in min_cal_dates.keys():
            # 按照trade_date和exchange作为联合主键，使用交易日历来获取没有采集的日期
            # 这会导致请求次数变多，但是可以保证数据的完整性，以及故障恢复的正确性
            trade_dates = [
                d.strftime('%Y%m%d')
                for d in conn.query_df(
                    f"""
                    SELECT DISTINCT cal_date
                    FROM trade_cal
                    WHERE cal_date NOT IN 
                    (SELECT `trade_date` FROM {self.get_table_name()} WHERE exchange = '{exchange}')
                        AND is_open = 1
                        AND cal_date >= '{min_cal_dates[exchange]}'
                        AND cal_date <= today()
                        AND exchange = '{exchange}'
                    ORDER BY cal_date
                                """
                )['cal_date']
            ]

            for trade_date in trade_dates:
                yield self.get_scrapy_request(params={"trade_date": trade_date, "exchange": exchange})


class FutSettleSpider(DailySpider):
    name = "future/quotes/fut_settle"
    custom_settings = {"TABLE_NAME": "fut_settle"}


class FutMappingSpider(DailySpider):
    name = "future/quotes/fut_mapping"
    custom_settings = {"TABLE_NAME": "fut_mapping"}


class FutWSRSpider(DailySpider):
    name = "future/quotes/fut_wsr"
    custom_settings = {"TABLE_NAME": "fut_wsr"}
