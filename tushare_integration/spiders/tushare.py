import datetime
import json
import typing
from typing import ClassVar, Generator, Literal

import httpx
import pandas as pd
from sqlalchemy import and_, not_, select

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


class TimeSeriesSpider(TushareSpider):
    __model__: type[Base] = Base
    __trade_date_period__: Literal["D", "W", "ME"] = "D"
    __trade_cal_model__: type[Base] = TradeCal

    def get_dates(self, freq: Literal['MS', 'W-MON', 'D'] = 'MS'):
        conn = self.get_db_engine()
        stmt = select(getattr(self.__model__, self.__trade_date_field__)).distinct()
        existing_df = conn.query_df(stmt)
        if not existing_df.empty:
            existing = set(
                existing_df[self.__trade_date_field__].apply(
                    lambda x: x.strftime("%Y%m%d") if isinstance(x, (datetime.date, datetime.datetime)) else str(x)
                )
            )
        else:
            existing = set()

        if not hasattr(self.__model__, '__start_date__') or self.__model__.__start_date__ is None:
            self.__model__.__start_date__ = '2008-01-01'

        start_date = pd.to_datetime(self.__model__.__start_date__, format="%Y-%m-%d")
        end_date = pd.to_datetime(datetime.date.today())
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        for date in dates:
            date_str = date.strftime("%Y%m%d")
            if date_str not in existing:
                yield self.get_httpx_request(params={"date": date_str})

    def get_trade_dates(self, period: Literal["D", "W", "ME"] | None = None) -> pd.DataFrame:
        if period is None:
            period = self.__trade_date_period__
        conn = self.get_db_engine()

        if not hasattr(self.__trade_cal_model__, 'is_open'):
            raise AttributeError("The model does not have a 'is_open' attribute.")
        if not hasattr(self.__trade_cal_model__, 'cal_date'):
            raise AttributeError("The model does not have a 'cal_date' attribute.")

        stmt = (
            select(getattr(self.__trade_cal_model__, 'cal_date'))
            .distinct()
            .where(
                and_(
                    getattr(self.__trade_cal_model__, 'is_open') == '1',
                    getattr(self.__trade_cal_model__, 'cal_date') <= datetime.datetime.today(),
                )
            )
            .order_by(getattr(self.__trade_cal_model__, 'cal_date'))
        )
        trade_dates = conn.query_df(stmt)
        if trade_dates.empty:
            return trade_dates

        trade_dates['cal_date'] = pd.to_datetime(trade_dates['cal_date'])
        trade_dates = (
            trade_dates.assign(trade_date_index=lambda x: x['cal_date'].astype('datetime64[ns]'))
            .set_index('trade_date_index')
            .resample(period)
            .agg({'cal_date': 'last'})
            .reset_index(drop=True)
            .dropna()
        )
        stmt = (
            select(getattr(self.__model__, self.__trade_date_field__))
            .distinct()
            .order_by(getattr(self.__model__, self.__trade_date_field__))
        )
        db_trade_dates = conn.query_df(stmt)
        if not db_trade_dates.empty:
            db_trade_dates[self.__trade_date_field__] = pd.to_datetime(db_trade_dates[self.__trade_date_field__])
            trade_dates = trade_dates[~trade_dates['cal_date'].isin(db_trade_dates[self.__trade_date_field__])]
        return trade_dates

    def start_requests(self):
        trade_dates_df = self.get_trade_dates()
        if trade_dates_df.empty:
            return
        for _, row in trade_dates_df.iterrows():
            trade_date = row['cal_date']
            yield self.get_httpx_request(params={self.__trade_date_field__: trade_date.strftime("%Y%m%d")})


class TSCodeSpider(TushareSpider):
    __model__: type[Base] = Base
    __basic_table__: type[Base] = StockBasic

    def start_requests(self):
        conn = self.get_db_engine()
        if not hasattr(self.__basic_table__, 'ts_code'):
            raise AttributeError("The model does not have a 'ts_code' attribute.")

        query = select(getattr(self.__basic_table__, 'ts_code')).distinct()
        ts_codes = conn.query_df(query)

        for ts_code in ts_codes['ts_code']:
            yield self.get_httpx_request(params={"ts_code": ts_code})


class FinancialReportSpider(TushareSpider):
    __model__: type[Base] = Base
    _api_name_override: str | None = None

    @property
    def api_name(self) -> str:
        return self._api_name_override or super().api_name

    @api_name.setter
    def api_name(self, value: str):
        self._api_name_override = value

    def start_requests(self):
        if self.settings.tushare_point >= 5000:
            return self.request_with_vip()
        else:
            return self.request_with_ts_code()

    @staticmethod
    def get_all_period():
        periods = []
        for year in range(1990, datetime.datetime.now().year + 1):
            for end_date in [f"{year}0331", f"{year}0630", f"{year}0930", f"{year}1231"]:
                periods.append(end_date)
        return periods

    def request_with_vip(self):
        if self.__model__.__has_vip__ is True:
            self.api_name = self.api_name + "_vip"
        for period in self.get_all_period():
            if self.api_name.startswith(("income", "balance", "cashflow")):
                for report_type in range(1, 13):
                    params = {"period": period, "report_type": str(report_type)}
                    yield self.get_httpx_request(params)
            else:
                params = {"period": period}
                yield self.get_httpx_request(params)

    def request_with_ts_code(self):
        conn = self.get_db_engine()
        query = select(StockBasic.ts_code)
        ts_codes = conn.query_df(query)['ts_code']

        for ts_code in ts_codes:
            params = {"ts_code": ts_code, "limit": 2000}
            yield self.get_httpx_request(params)


class LimitOffsetSpider(TushareSpider):
    __limit__: int = 5000

    def start_requests(self) -> Generator[httpx.Request, typing.Any, None]:
        yield self.get_httpx_request(params={'offset': 0, 'limit': self.__limit__})

    def _has_more(self, response: httpx.Response) -> bool:
        try:
            return response.json().get('data', {}).get('has_more', False) == True
        except Exception as e:
            logger.error("Error parsing response: %s", e)
            return False

    def parse(self, response: httpx.Response, **kwargs):
        first_page = self.parse_response(response, **kwargs)
        if first_page.empty:
            return None

        all_data = [first_page]
        base_params = response.request.extensions.get("params", {})
        offset = base_params.get('offset', 0)
        limit = base_params.get('limit', self.__limit__)

        while self._has_more(response):
            offset += limit
            params = base_params.copy()
            params.update({'offset': offset, 'limit': limit})
            next_request = self.get_httpx_request(params=params)
            response = self._process_request(next_request)

            next_page = self.parse_response(response, **kwargs)
            if next_page.empty:
                break
            all_data.append(next_page)

        return pd.concat(all_data, ignore_index=True)
