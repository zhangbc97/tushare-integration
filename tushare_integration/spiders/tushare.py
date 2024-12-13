import datetime
import json
import logging
from typing import ClassVar

import pandas as pd
import requests
import scrapy
import yaml
from sqlalchemy import and_, not_, select, text

from tushare_integration.db_engine import DBEngine
from tushare_integration.items import TushareIntegrationItem
from tushare_integration.models.core.base import Base
from tushare_integration.models.stock_basic import StockBasic
from tushare_integration.models.trade_cal import TradeCal
from tushare_integration.settings import TushareIntegrationSettings


class TushareSpiderMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        if not hasattr(cls, '__model__'):
            raise ValueError(f"类 {name} 必须设置 __model__ 属性")
        # 为每个非Base的model设置name，即使已经有name属性也要重新设置
        model = getattr(cls, '__model__')
        if model is not Base:
            setattr(cls, 'name', model.__api_name__)
        return cls


class TushareSpider(scrapy.Spider, metaclass=TushareSpiderMeta):
    __spider_name__: str
    __model__: ClassVar[type[Base]] = Base
    name: ClassVar[str]  # 添加name的类型声明

    spider_settings: TushareIntegrationSettings
    db_engine: DBEngine
    custom_settings: dict = {}

    @property
    def api_name(self) -> str:
        return self.__model__.__api_name__

    @property
    def table_name(self) -> str:
        return self.__model__.__tablename__

    @property
    def start_date(self) -> str | None:
        return self.__model__.__start_date__

    @property
    def fields(self) -> str:
        return ",".join([column.name for column in self.__model__.__table__.columns])

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        spider.spider_settings = TushareIntegrationSettings.model_validate(
            yaml.safe_load(open('config.yaml', 'r', encoding='utf8').read())
        )
        spider.create_table()
        return spider

    def create_table(self):
        logging.info(f"quest {self.name}: create table {self.table_name}")
        self.db_engine = DBEngine(self.spider_settings)
        self.db_engine.create_table(self.__model__)

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        start_date = self.start_date or '19900101'

        # 构建子查询
        trade_date_field = self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date')
        subquery = select(text(f"`{trade_date_field}`")).select_from(text(f"{db_name}.{self.table_name}"))

        # 构建主查询
        query = (
            select(TradeCal.cal_date.distinct())
            .where(
                and_(
                    not_(TradeCal.cal_date.in_(subquery)),
                    TradeCal.is_open == 1,
                    TradeCal.cal_date >= start_date,
                    TradeCal.cal_date <= datetime.datetime.now().strftime("%Y%m%d"),
                    TradeCal.exchange == 'SSE',
                )
            )
            .order_by(TradeCal.cal_date)
        )

        cal_dates = conn.query_df(query)

        if cal_dates.empty:
            return

        trade_dates = [cal_date.strftime("%Y%m%d") for cal_date in cal_dates["cal_date"]]

        for trade_date in trade_dates:
            yield self.get_scrapy_request(
                params={self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date'): trade_date}
            )

    def parse(self, response, **kwargs):
        item = self.parse_response(response, **kwargs)

        if item['data'] is None or len(item['data']) == 0:
            return

        return item

    def parse_response(self, response, **kwargs):
        resp = json.loads(response.text)

        if resp["code"] != 0:
            logging.error(f"Request {self.api_name} failed: {resp['msg']}")
            raise RuntimeError(resp['msg'])

        return TushareIntegrationItem(data=pd.DataFrame(data=resp["data"]["items"], columns=resp["data"]["fields"]))

    def get_db_engine(self):
        return self.db_engine

    def get_scrapy_request(self, params: dict | None = None, meta: dict | None = None):
        if not params:
            params = {}

        if not meta:
            meta = {}

        logging.info(f"Requesting {self.api_name} with params: {params}")

        return scrapy.Request(
            url=self.spider_settings.tushare_url,
            method="POST",
            body=json.dumps(
                {
                    "api_name": self.api_name,
                    "token": self.spider_settings.tushare_token,
                    "params": params,
                    "fields": self.fields,
                }
            ),
            headers={
                "Content-Type": "application/json",
            },
            meta={
                'api_name': self.api_name,
                'params': params,
            }
            | meta,
        )

    # 搞个函数，直接使用requests发起请求
    def request_with_requests(self, params: dict | None = None, meta: dict | None = None) -> TushareIntegrationItem:
        logging.info(f"Requesting {self.api_name} with params: {params}")
        response = requests.post(
            url=self.spider_settings.tushare_url,
            json={
                "api_name": self.api_name,
                "token": self.spider_settings.tushare_token,
                "params": params,
                "fields": self.fields,
            },
            headers={
                "Content-Type": "application/json",
            },
        )

        return self.parse_response(response)


class DailySpider(TushareSpider):
    __model__: type[Base] = Base
    custom_settings: dict[str, str] = {"TRADE_DATE_FIELD": "trade_date"}

    def start_requests(self):
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name
        start_date = self.start_date or '1990-01-01'

        # 构建子查询
        trade_date_field = self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date')
        subquery = select(text(f"`{trade_date_field}`")).select_from(text(f"{db_name}.{self.table_name}"))

        # 构建主查询
        query = (
            select(TradeCal.cal_date.distinct())
            .where(
                and_(
                    not_(TradeCal.cal_date.in_(subquery)),
                    TradeCal.is_open == 1,
                    TradeCal.cal_date >= start_date,
                    TradeCal.cal_date <= datetime.datetime.now().strftime("%Y%m%d"),
                    TradeCal.exchange == 'SSE',
                )
            )
            .order_by(TradeCal.cal_date)
        )

        cal_dates = conn.query_df(query)

        if cal_dates.empty:
            return

        trade_dates = [cal_date.strftime("%Y%m%d") for cal_date in cal_dates["cal_date"]]

        for trade_date in trade_dates:
            yield self.get_scrapy_request(
                params={self.custom_settings.get('TRADE_DATE_FIELD', 'trade_date'): trade_date}
            )


class TSCodeSpider(TushareSpider):
    __model__: type[Base] = Base
    custom_settings: dict[str, str] = {'BASIC_TABLE': 'stock_basic'}

    def start_requests(self):
        table_name = self.custom_settings.get('BASIC_TABLE')
        conn = self.get_db_engine()
        db_name = self.spider_settings.database.db_name

        # 使用 SQLAlchemy select
        query = select(text('ts_code')).select_from(text(f"{db_name}.{table_name}"))
        ts_codes = conn.query_df(query)

        for ts_code in ts_codes['ts_code']:
            yield self.get_scrapy_request(params={"ts_code": ts_code})


class FinancialReportSpider(TushareSpider):
    __model__: type[Base] = Base
    _api_name_override: str | None = None  # 新增用于存储覆盖的api_name

    @property
    def api_name(self) -> str:
        return self._api_name_override or super().api_name

    @api_name.setter
    def api_name(self, value: str):
        self._api_name_override = value

    def start_requests(self):
        # 如果积分大于5000，使用vip接口
        if self.spider_settings.tushare_point >= 5000:
            return self.request_with_vip()
        else:
            return self.request_with_ts_code()

    @staticmethod
    def get_all_period():
        # 取所有的period
        periods = []
        for year in range(1990, datetime.datetime.now().year + 1):
            for end_date in [f"{year}0331", f"{year}0630", f"{year}0930", f"{year}1231"]:
                periods.append(end_date)
        return periods

    def request_with_vip(self):
        # 每次全量同步即可，30年的数据只有4*30*12=1440次请求
        if self.__model__.__has_vip__ is True:
            self.api_name = self.api_name + "_vip"
        for period in self.get_all_period():
            # 三大报表需要按照report_type分别请求
            if self.api_name.startswith(("income", "balance", "cashflow")):
                for report_type in range(1, 13):
                    params = {"period": period, "report_type": str(report_type)}
                    yield self.get_scrapy_request(params)
            else:
                # 其他报表只需按period请求即可
                params = {"period": period}
                yield self.get_scrapy_request(params)

    def request_with_ts_code(self):
        # 按ts_code取数据，每次取一个股票的全量，几千次请求
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 ts_code
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            params = {"ts_code": ts_code, "limit": 2000}
            yield self.get_scrapy_request(params)
