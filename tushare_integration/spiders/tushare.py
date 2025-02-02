import datetime
import json
from typing import ClassVar, Generator

import httpx
import pandas as pd
from sqlalchemy import and_, not_, select, text

from tushare_integration.crawler.spider import Spider
from tushare_integration.db_engine import DBEngine
from tushare_integration.logger import get_logger
from tushare_integration.models.core.base import Base
from tushare_integration.models.stock_basic import StockBasic
from tushare_integration.models.trade_cal import TradeCal
from tushare_integration.settings import TushareIntegrationSettings

logger = get_logger()

class TushareSpider(Spider):
    __spider_name__: str
    __model__: ClassVar[type[Base]] = Base
    __trade_date_field__: str = 'trade_date'

    def __init__(self, settings: TushareIntegrationSettings):
        super().__init__(settings)
        self.db_engine: DBEngine = DBEngine(settings)

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

    def start_requests(self):
        yield self.get_httpx_request()

    def parse(self, response: httpx.Response, **kwargs) -> Generator[pd.DataFrame, None, None]:
        data = self.parse_response(response, **kwargs)

        if data is None or data.empty:
            return

        yield data

    def parse_response(self, response, **kwargs) -> pd.DataFrame:
        resp = json.loads(response.text)

        if resp["code"] != 0:
            logger.error("Request %s failed: %s", self.api_name, resp['msg'])
            raise RuntimeError(resp['msg'])

        return pd.DataFrame(data=resp["data"]["items"], columns=resp["data"]["fields"])

    def get_db_engine(self):
        return self.db_engine

    def get_httpx_request(self, params: dict | None = None, extensions: dict | None = None):
        if not params:
            params = {}

        if not extensions:
            extensions = {}

        logger.debug("Build Request for %s with params: %s", self.api_name, params)

        return httpx.Request(
            url=self.settings.tushare_url,
            method="POST",
            json={
                "api_name": self.api_name,
                "token": self.settings.tushare_token,
                "params": params,
                "fields": self.fields,
            },
            headers={
                "Content-Type": "application/json",
            },
            extensions={
                'api_name': self.api_name,
                'params': params,
            }
            | extensions,
        )


class DailySpider(TushareSpider):
    __model__: type[Base] = Base

    def start_requests(self):
        conn = self.get_db_engine()
        start_date = self.start_date or datetime.date(1990, 1, 1)

        # 重构后：直接使用 ORM 模型属性构造查询
        subquery = select(getattr(self.__model__, self.__trade_date_field__)).select_from(self.__model__)

        query = (
            select(TradeCal.cal_date.distinct())
            .where(
                and_(
                    not_(TradeCal.cal_date.in_(subquery)),
                    TradeCal.is_open == '1',
                    TradeCal.cal_date >= start_date,
                    TradeCal.cal_date <= datetime.date.today(),
                    TradeCal.exchange == 'SSE',
                )
            )
            .order_by(TradeCal.cal_date)
        )

        cal_dates = conn.query_df(query)

        if cal_dates.empty:
            return

        cal_dates["cal_date"] = pd.to_datetime(cal_dates["cal_date"])

        trade_dates = [cal_date.strftime("%Y%m%d") for cal_date in cal_dates["cal_date"]]

        for trade_date in trade_dates:
            yield self.get_httpx_request(params={self.__trade_date_field__: trade_date})


class TSCodeSpider(TushareSpider):
    __model__: type[Base] = Base
    __basic_table__: type[Base] = StockBasic

    def start_requests(self):
        conn = self.get_db_engine()
        # 使用ORM模型构造查询，从动态引用的 __basic_table__ 中获取 ts_code 字段

        if not hasattr(self.__basic_table__, 'ts_code'):
            raise AttributeError("The model does not have a 'ts_code' attribute.")

        query = select(getattr(self.__basic_table__, 'ts_code'))
        ts_codes = conn.query_df(query)

        for ts_code in ts_codes['ts_code']:
            yield self.get_httpx_request(params={"ts_code": ts_code})


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
        if self.settings.tushare_point >= 5000:
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
                    yield self.get_httpx_request(params)
            else:
                # 其他报表只需按period请求即可
                params = {"period": period}
                yield self.get_httpx_request(params)

    def request_with_ts_code(self):
        # 按ts_code取数据，每次取一个股票的全量，几千次请求
        conn = self.get_db_engine()

        # 使用 SQLAlchemy select 获取所有的 ts_code
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            params = {"ts_code": ts_code, "limit": 2000}
            yield self.get_httpx_request(params)
