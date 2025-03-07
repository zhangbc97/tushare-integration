import datetime

import httpx
import pandas as pd
from sqlalchemy import and_, select
from sqlalchemy.sql import func
from tushare_models.opt_basic import OptBasic
from tushare_models.opt_daily import OptDaily
from tushare_models.opt_mins import OptMins

from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider, get_logger

logger = get_logger()


# 期权基础信息 Spider，用于采集期权的静态基础数据
class OptBasicSpider(TushareSpider):
    __model__: type[OptBasic] = OptBasic

    def start_requests(self):
        for exchange in ["SSE", "SZSE", "CFFEX", "DCE", "CZCE", "SHFE", "INE"]:
            params = {"exchange": exchange}
            yield self.get_httpx_request(params)


# 期权日线行情 Spider，用于采集期权日线行情数据
# 该接口每天数据量可能超过15000条，使用 LimitOffsetSpider 分页处理
class OptDailySpider(LimitOffsetSpider, TimeSeriesSpider):
    __model__: type[OptDaily] = OptDaily
    __limit__: int = 15000

    def start_requests(self):
        for trade_date in self.get_trade_dates('D'):
            yield self.get_httpx_request(params={"trade_date": trade_date})


class OptMinsSpider(TimeSeriesSpider):
    __model__: type[OptMins] = OptMins

    def start_requests(self):
        # 检查模型类型是否正确
        if not self.__model__ is OptMins:
            raise ValueError("OptMins is the only supported model for this spider")
        # 从期权基础信息表获取所有期权代码，假设字段名为 ts_code
        query = select(OptBasic.ts_code)
        ts_codes = self.get_db_engine().query_df(query)['ts_code']
        for ts_code in ts_codes:
            # 查询该期权已采集的交易日期
            exists_date_df = self.get_db_engine().query_df(
                select(func.to_date(self.__model__.trade_time).label('trade_date'))
                .distinct()
                .where(self.__model__.ts_code == ts_code)
            )
            if exists_date_df.empty:
                exists_date = []
            else:
                exists_date = list(exists_date_df['trade_date'].dt.date)
            # 根据期权日线数据来确定需要采集的交易日期，从 __start_date__ 开始
            trade_date_query = (
                select(OptDaily.trade_date)
                .distinct()
                .where(and_(OptDaily.ts_code == ts_code, OptDaily.trade_date >= self.__model__.__start_date__))
                .order_by(OptDaily.trade_date)
            )
            trade_dates_df = self.get_db_engine().query_df(trade_date_query)
            if trade_dates_df.empty:
                continue
            trade_dates = list(trade_dates_df['trade_date'].dt.date)
            last_end_date = None
            for trade_date in trade_dates:
                if trade_date in exists_date:
                    continue
                if last_end_date and trade_date <= last_end_date:
                    continue
                yield self.get_httpx_request(
                    params={
                        "ts_code": ts_code,
                        "start_date": trade_date.strftime("%Y-%m-%d") + " 09:00:00",
                        "end_date": (trade_date + datetime.timedelta(days=40)).strftime("%Y-%m-%d") + " 16:00:00",
                        "freq": "1min",
                    },
                    extensions={'exists_date': exists_date},
                )
                last_end_date = trade_date + datetime.timedelta(days=40)

    def parse(self, response: httpx.Response, **kwargs):
        exists_date = response.request.extensions.get('exists_date', [])
        data: pd.DataFrame = self.parse_response(response)
        if data.empty or len(data) == 0:
            return
        # 确保 trade_time 字段为 datetime 类型
        data['trade_time'] = data['trade_time'].astype(str)
        data['trade_time'] = pd.to_datetime(data['trade_time'])
        pipe_item = pd.DataFrame()
        # 按交易日期分组处理
        # 期权分钟数据条数可能不固定，不再严格校验是否为241条
        for trade_date, group in data.groupby(data['trade_time'].dt.date):
            if trade_date in exists_date:
                continue
            pipe_item = pd.concat([pipe_item, group])
        yield pipe_item
