import datetime
import json
import logging

import pandas as pd
import scrapy
import yaml
from sqlalchemy import create_engine, text

from tushare_integration.items import TushareIntegrationItem


class TushareSpider(scrapy.Spider):
    name = None
    api_name: str = None

    def start_requests(self):
        yield self.get_scrapy_request()

    def parse(self, response, **kwargs):
        return self.parse_response(response, **kwargs)

    def parse_response(self, response, **kwargs):
        resp = json.loads(response.text)

        if resp["code"] != 0:
            raise ValueError(resp["msg"])

        return TushareIntegrationItem(
            data=pd.DataFrame(
                data=resp["data"]["items"], columns=resp["data"]["fields"]
            )
        )

    def get_db_conn(self):
        return create_engine(self.settings.get("DB_URI")).connect()

    def get_scrapy_request(self, params: dict = None):
        if not params:
            params = {}

        logging.info(f"Requesting {self.get_api_name()} with params: {params}")

        return scrapy.Request(
            url=self.settings.get("TUSHARE_URL"),
            method="POST",
            body=json.dumps(
                {
                    "api_name": self.get_api_name(),
                    "token": self.settings.get("TUSHARE_TOKEN"),
                    "params": params,
                    "fields": self.load_fields(),
                }
            ),
            headers={
                "Content-Type": "application/json",
            },
        )

    def load_fields(self):
        with open(
                f"tushare_integration/schema/{self.get_schema_name()}.yaml", "r", encoding="utf-8"
        ) as f:
            schema = yaml.safe_load(f.read())
            return ",".join([column["name"] for column in schema["outputs"]])

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
    custom_settings = {"TABLE_NAME": "daily"}

    def start_requests(self):
        min_cal_date = self.custom_settings.get("MIN_CAL_DATE", '1970-01-01')
        conn = self.get_db_conn()
        db_name = self.settings.get("DB_NAME")

        trade_dates = [
            cal_date[0].strftime("%Y%m%d")
            for cal_date in conn.execute(
                text(f"""
                SELECT DISTINCT cal_date
                FROM {db_name}.trade_cal
                WHERE cal_date NOT IN (SELECT `trade_date` FROM {db_name}.{self.get_table_name()})
                  AND is_open = 1
                  AND cal_date >= '{min_cal_date}'
                  AND cal_date <= today()
                  AND exchange = 'SSE'
                ORDER BY cal_date
                """)  # 期货交易日历共享同一张表，所以这里过滤SSE
            ).all()
        ]

        for trade_date in trade_dates:
            yield self.get_scrapy_request(
                params={"trade_date": trade_date}
            )


class TSCodeSpider(TushareSpider):
    name = None

    custom_settings = {'BASIC_TABLE': 'stock_basic'}

    def start_requests(self):
        table_name = self.custom_settings.get('BASIC_TABLE')
        conn = self.get_db_conn()
        db_name = self.settings.get("DB_NAME")

        ts_codes = [
            row[0]
            for row in conn.execute(
                text(f"""
                SELECT ts_code FROM {db_name}.{table_name}
                """)
            ).fetchall()
        ]

        for ts_code in ts_codes:
            yield self.get_scrapy_request(params={"ts_code": ts_code})


class FinancialReportSpider(TushareSpider):
    name = None
    api_name = "financial_report"

    def start_requests(self):
        # 如果积分大于5000，使用vip接口
        if self.settings.get('TUSHARE_POINT', 2000) >= 5000:
            return self.request_with_vip()
        else:
            return self.request_with_ts_code()

    @staticmethod
    def get_all_period():
        # 获取所有的period
        periods = []
        for year in range(2022, datetime.datetime.now().year):
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
        conn = self.get_db_conn()
        db_name = self.settings.get("DB_NAME")
        ts_codes = [row[0] for row in conn.execute(f'''
            SELECT ts_code FROM {db_name}.stock_basic
        ''').fetchall()]

        for ts_code in ts_codes:
            params = {"ts_code": ts_code, "limit": 2000}
            yield self.get_scrapy_request(params)
