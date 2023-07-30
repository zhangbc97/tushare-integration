import datetime
import json
import logging

import pandas as pd
import scrapy
import yaml

from tushare_integration.db_engine import DatabaseEngineFactory, DBEngine
from tushare_integration.items import TushareIntegrationItem
from tushare_integration.settings import TushareIntegrationSettings


class TushareSpider(scrapy.Spider):
    name = None
    api_name: str = None
    schema = None
    spider_settings: TushareIntegrationSettings = None  # 不能直接叫settings，会覆盖掉scrapy的settings
    db_engine: DBEngine = None

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.schema = self.get_schema()

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.spider_settings = TushareIntegrationSettings.parse_file('config.yaml')
        spider.create_table()
        return spider

    def create_table(self):
        logging.info(f"create table {self.get_table_name()}")

        self.db_engine = DatabaseEngineFactory.create(self.spider_settings)
        self.db_engine.create_table(self.get_table_name(), self.schema)

    def get_schema(self):
        with open(
                f"tushare_integration/schema/{self.get_schema_name()}.yaml", "r", encoding="utf-8"
        ) as f:
            return yaml.safe_load(f.read())

    def start_requests(self):
        yield self.get_scrapy_request()

    def parse(self, response, **kwargs):
        item = self.parse_response(response, **kwargs)

        if item['data'] is None or len(item['data']) == 0:
            return

        return item

    def parse_response(self, response, **kwargs):
        resp = json.loads(response.text)

        if resp["code"] != 0:
            logging.error(f"Request {self.get_api_name()} failed: {resp['msg']}")
            raise RuntimeError(resp['msg'])

        return TushareIntegrationItem(
            data=pd.DataFrame(
                data=resp["data"]["items"], columns=resp["data"]["fields"]
            )
        )

    def get_db_engine(self):
        return self.db_engine

    def get_scrapy_request(self, params: dict = None, meta: dict = None):
        if not params:
            params = {}

        if not meta:
            meta = {}

        logging.info(f"Requesting {self.get_api_name()} with params: {params}")

        return scrapy.Request(
            url=self.spider_settings.tushare_url,
            method="POST",
            body=json.dumps(
                {
                    "api_name": self.get_api_name(),
                    "token": self.spider_settings.tushare_token,
                    "params": params,
                    "fields": self.load_fields(),
                }
            ),
            headers={
                "Content-Type": "application/json",
            },
            meta={
                     'api_name': self.get_api_name(),
                     'params': params,
                 } | meta
        )

    def load_fields(self):
        return ",".join([column["name"] for column in self.schema["outputs"]])

    def get_schema_name(self):
        return self.name

    def get_api_name(self):
        if self.api_name:
            return self.api_name
        return self.name.split("/")[-1]

    def get_table_name(self):
        if self.custom_settings and self.custom_settings.get("TABLE_NAME"):
            return self.custom_settings.get("TABLE_NAME")
        return self.name.split("/")[-1]


class DailySpider(TushareSpider):
    name = None
    custom_settings = {"TABLE_NAME": "daily", "TRADE_DATE_FIELD": "trade_date"}

    def start_requests(self):
        min_cal_date = self.custom_settings.get("MIN_CAL_DATE", '1970-01-01')
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name

        cal_dates = conn.query_df(
            f"""
                SELECT DISTINCT cal_date
                FROM {db_name}.trade_cal
                WHERE cal_date NOT IN (SELECT `{self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date')}` FROM {db_name}.{self.get_table_name()})
                  AND is_open = 1
                  AND cal_date >= '{min_cal_date}'
                  AND cal_date <= today()
                  AND exchange = 'SSE'
                ORDER BY cal_date
                """  # 期货交易日历共享同一张表，所以这里过滤SSE
        )

        if cal_dates.empty:
            return

        trade_dates = [
            cal_date.strftime("%Y%m%d") for cal_date in cal_dates["cal_date"]
        ]

        for trade_date in trade_dates:
            yield self.get_scrapy_request(
                params={self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date'): trade_date}
            )


class TSCodeSpider(TushareSpider):
    name = None

    custom_settings = {'BASIC_TABLE': 'stock_basic'}

    def start_requests(self):
        table_name = self.custom_settings.get('BASIC_TABLE')
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name

        ts_codes = conn.query_df(f"SELECT ts_code FROM {db_name}.{table_name}")

        for ts_code in ts_codes:
            yield self.get_scrapy_request(params={"ts_code": ts_code})


class FinancialReportSpider(TushareSpider):
    name = None
    api_name = "financial_report"

    def start_requests(self):
        # 如果积分大于5000，使用vip接口
        if self.spider_settings.tushare_point >= 5000:
            return self.request_with_vip()
        else:
            return self.request_with_ts_code()

    @staticmethod
    def get_all_period():
        # 获取所有的period
        periods = []
        for year in range(1990, datetime.datetime.now().year):
            for end_date in [f"{year}0331", f"{year}0630", f"{year}0930", f"{year}1231"]:
                periods.append(end_date)
        return periods

    def request_with_vip(self):
        # 每次全量同步即可，30年的数据只有4*30*12=1440次请求
        # 尽管实测半个小时同步完，但是毕竟离线数据，慢点也无妨，后期如果需要再进行优化
        self.api_name = self.api_name + "_vip"
        for period in self.get_all_period():
            # 三大报表需要按照report_type分别请求
            if self.api_name.startswith(("income", "balance", "cashflow")):
                for report_type in range(1, 13):
                    params = {"period": period, "report_type": str(report_type)}
                    yield self.get_scrapy_request(params)
            else:
                # 其他报表只需要按period请求即可
                params = {"period": period}
                yield self.get_scrapy_request(params)

    def request_with_ts_code(self):
        # 按ts_code取数据，每次取一个股票的全量，几千次请求
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        ts_codes = conn.query_df(f' SELECT ts_code FROM {db_name}.stock_basic')['ts_code']

        for ts_code in ts_codes:
            params = {"ts_code": ts_code, "limit": 2000}
            yield self.get_scrapy_request(params)
