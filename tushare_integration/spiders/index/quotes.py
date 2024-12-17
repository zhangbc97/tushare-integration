import datetime

from tushare_integration.spiders.stock.quotes import StockMonthlySpider, StockWeeklySpider
from tushare_integration.spiders.tushare import DailySpider, TushareSpider


class IndexDailySpider(DailySpider):
    name = "index/quotes/index_daily"
    custom_settings = {"TABLE_NAME": "index_daily", 'BASIC_TABLE': 'index_basic'}

    def start_requests(self):
        # index_daily需要特殊处理，这个接口不支持按日期获取数据，这意味着需要用ts_code去取
        # 接口一次性最大返回8000条数据，部分指数的数据量超过8000条，所以需要分批取
        # 到2024年最多的一年只有257个交易日，我们按一年260个交易日来计算，一次可以取30年的数据
        # 看了一下实际上现在就3000多个指数，全请求一次也就不到8000次，直接全量取吧
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        index_list = conn.query_df(f"select * from {db_name}.{self.custom_settings.get('BASIC_TABLE')}")

        if index_list.empty:
            return

        # 从base_date开始取，一次+30年
        for _, row in index_list.iterrows():
            ts_code = row["ts_code"]
            start_date = row["base_date"].date()
            end_date = start_date + datetime.timedelta(days=30 * 365)

            while True:
                if start_date > datetime.date.today():
                    break

                yield self.get_scrapy_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": start_date.strftime("%Y%m%d"),
                        "end_date": end_date.strftime("%Y%m%d"),
                    }
                )
                start_date = end_date
                end_date = start_date + datetime.timedelta(days=30 * 365)


class DailyInfoSpider(DailySpider):
    name = "index/quotes/daily_info"
    custom_settings = {"TABLE_NAME": "daily_info"}


# noinspection SpellCheckingInspection
class IndexDailyBasicSpider(DailySpider):
    name = "index/quotes/index_dailybasic"
    custom_settings = {"TABLE_NAME": "index_dailybasic"}


class IndexGlobalSpider(DailySpider):
    name = "index/quotes/index_global"
    custom_settings = {"TABLE_NAME": "index_global"}


class IndexMonthlySpider(StockMonthlySpider):
    name = "index/quotes/index_monthly"
    custom_settings = {"TABLE_NAME": "index_monthly"}


class IndexWeeklySpider(StockWeeklySpider):
    name = "index/quotes/index_weekly"
    custom_settings = {"TABLE_NAME": "index_weekly"}


class IndexWeightSpider(TushareSpider):
    name = "index/quotes/index_weight"
    custom_settings = {
        "TABLE_NAME": "index_weight",
        "BASIC_TABLE": "index_basic",
    }

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        db_type = self.spider_settings.database.db_type.lower()
        
        # 1. 获取所有指数列表
        index_list = conn.query_df(f"select * from {db_name}.{self.custom_settings.get('BASIC_TABLE')}")
        if index_list.empty:
            self.logger.warning("指数基础信息表为空，请先运行 index/basic/index_basic 爬虫")
            return

        # 2. 根据数据库类型使用不同的日期截断SQL
        date_trunc_sql = {
            'mysql': "DATE_FORMAT(trade_date, '%Y-%m-01')",
            'clickhouse': "toStartOfMonth(trade_date)",
            'postgresql': "date_trunc('month', trade_date)"
        }.get(db_type, "date_trunc('month', trade_date)")

        existing_data = conn.query_df(f"""
            SELECT 
                index_code,
                {date_trunc_sql} as month
            FROM {db_name}.{self.custom_settings.get('TABLE_NAME')}
            GROUP BY index_code, {date_trunc_sql}
        """)
        
        # 将结果转换为集合，用于快速查找某个指数某月是否有数据
        existing_months = {
            (row['index_code'], row['month'].date() if isinstance(row['month'], datetime.datetime) else row['month'])
            for _, row in existing_data.iterrows()
        } if not existing_data.empty else set()

        # 3. 按月生成请求
        today = datetime.date.today()
        today = today.replace(day=1)  # 调整到当月第一天
        
        for _, row in index_list.iterrows():
            index_code = row["ts_code"]
            
            # 获取该指数的起始日期
            start_date = row["list_date"].date() if row["list_date"] else row["base_date"].date()
            start_date = start_date.replace(day=1)  # 调整到月初
            
            # 按月生成请求
            while start_date <= today:
                # 检查这个月是否已有完整数据
                if (index_code, start_date) not in existing_months:
                    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
                    
                    yield self.get_scrapy_request(
                        params={
                            "index_code": index_code,
                            "start_date": start_date.strftime("%Y%m%d"),
                            "end_date": end_date.strftime("%Y%m%d"),
                        }
                    )
                
                start_date = (start_date + datetime.timedelta(days=32)).replace(day=1)


class SzDailyInfoSpider(DailySpider):
    name = "index/quotes/sz_daily_info"
    custom_settings = {"TABLE_NAME": "sz_daily_info", ' MIN_CAL_DATE': '2008-01-02'}
