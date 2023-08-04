import datetime

from tushare_integration.spiders.tushare import DailySpider, TushareSpider, TSCodeSpider


class ReportRCSpider(TSCodeSpider):
    # 更新日期不固定，定期用TSCodeSpider更新
    name = "stock/special/report_rc"
    api_name = "report_rc"
    custom_settings = {"TABLE_NAME": "report_rc", "BASIC_TABLE": "stock_basic"}


class CyqPerfSpider(DailySpider):
    name = "stock/special/cyq_perf"
    api_name = "cyq_perf"
    custom_settings = {"TABLE_NAME": "cyq_perf"}


class CyqChipsSpider(TushareSpider):
    name = "stock/special/cyq_chips"
    api_name = "cyq_chips"
    custom_settings = {"TABLE_NAME": "cyq_chips", "BASIC_TABLE": "stock_basic", "MIN_CAL_DATE": "2010-01-01"}

    def start_requests(self):
        conn = self.get_db_engine()
        for ts_code in conn.query_df(
                f""" SELECT ts_code FROM {self.spider_settings.database.db_name}.{self.custom_settings.get("BASIC_TABLE")}"""
        )['ts_code']:
            # 查询在daily中出现，但是在cyq_chips中没有的trade_date
            trade_dates = conn.query_df(
                f"""
                    SELECT DISTINCT trade_date 
                    FROM {self.spider_settings.database.db_name}.daily
                    WHERE ts_code = '{ts_code}' 
                    AND trade_date >= '{self.custom_settings.get("MIN_CAL_DATE")}'
                    AND trade_date NOT IN (
                        SELECT DISTINCT trade_date FROM {self.spider_settings.database.db_name}.{self.get_table_name()}
                        WHERE ts_code = '{ts_code}'
                    )"""
            )

            if trade_dates.empty:
                continue

            for trade_date in trade_dates['trade_date'].dt.date:
                yield self.get_scrapy_request(
                    {"ts_code": ts_code, "trade_date": trade_date.strftime("%Y%m%d")}
                )


class StkFactorSpider(DailySpider):
    name = "stock/special/stk_factor"
    api_name = "stk_factor"
    custom_settings = {"TABLE_NAME": "stk_factor"}


class CCASSHoldSpider(DailySpider):
    name = "stock/special/ccass_hold"
    api_name = "ccass_hold"
    custom_settings = {"TABLE_NAME": "ccass_hold", "MIN_CAL_DATE": "2020-11-11"}


class CCASSHoldDetailSpider(DailySpider):
    name = "stock/special/ccass_hold_detail"
    api_name = "ccass_hold_detail"
    custom_settings = {"TABLE_NAME": "ccass_hold_detail", "MIN_CAL_DATE": "2016-12-05"}


class HKHoldSpider(DailySpider):
    name = "stock/special/hk_hold"
    api_name = "hk_hold"
    custom_settings = {"TABLE_NAME": "hk_hold"}


class LimitListDailySpider(DailySpider):
    name = "stock/special/limit_list_d"
    api_name = "limit_list_d"
    custom_settings = {"TABLE_NAME": "limit_list_d"}


class StkSurvSpider(TSCodeSpider):
    name = "stock/special/stk_surv"
    api_name = "stk_surv"
    custom_settings = {"TABLE_NAME": "stk_surv", "BASIC_TABLE": "stock_basic"}


class BrokerRecommend(TushareSpider):
    name = "stock/special/broker_recommend"
    api_name = "broker_recommend"
    custom_settings = {"TABLE_NAME": "broker_recommend"}

    def start_requests(self):
        # 生成从202003到现在的月份列表
        month_list = []
        for year in range(2020, datetime.datetime.now().year + 1):
            for month in range(1, 13):
                yield self.get_scrapy_request({"month": f"{year}{month:02d}"})
