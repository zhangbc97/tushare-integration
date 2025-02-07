import datetime
from typing import Literal

import pandas as pd
from sqlalchemy import select

from tushare_integration.models.bo_cinema import BoCinema
from tushare_integration.models.bo_daily import BoDaily
from tushare_integration.models.bo_monthly import BoMonthly
from tushare_integration.models.bo_weekly import BoWeekly
from tushare_integration.models.film_record import FilmRecord
from tushare_integration.models.teleplay_record import TeleplayRecord
from tushare_integration.models.tmt_twincome import TmtTwincome
from tushare_integration.models.tmt_twincomedetail import TmtTwincomedetail
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider


class TmtTwincomeSpider(LimitOffsetSpider):
    __model__: type[TmtTwincome] = TmtTwincome
    __limit__: int = 30

    def start_requests(self):
        for item in range(1, 66):
            yield self.get_httpx_request(params={"item": item, "offset": 0, "limit": self.__limit__})


class TmtTwincomeDetailSpider(LimitOffsetSpider):
    __model__: type[TmtTwincomedetail] = TmtTwincomedetail
    __limit__: int = 30

    def start_requests(self):
        for item in range(1, 66):
            yield self.get_httpx_request(params={"item": item, "offset": 0, "limit": self.__limit__})


class BoMonthlySpider(TimeSeriesSpider):
    __model__: type[BoMonthly] = BoMonthly
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('MS'):
            yield request


class BoWeeklySpider(TimeSeriesSpider):
    __model__: type[BoWeekly] = BoWeekly
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('W-MON'):
            yield request


class BoDailySpider(TimeSeriesSpider):
    __model__: type[BoDaily] = BoDaily
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('D'):
            yield request


class BoCinemaSpider(TimeSeriesSpider):
    __model__: type[BoCinema] = BoCinema
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('D'):
            yield request


class FilmRecordSpider(LimitOffsetSpider):
    __model__: type[FilmRecord] = FilmRecord
    __limit__: int = 500


class TeleplayRecordSpider(LimitOffsetSpider):
    __model__: type[TeleplayRecord] = TeleplayRecord
    __limit__: int = 1000
