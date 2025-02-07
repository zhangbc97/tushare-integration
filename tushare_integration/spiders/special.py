from datetime import datetime, timedelta
from typing import Any, Generator, Type

import httpx
from sqlalchemy import and_, func, select

from tushare_integration.logger import get_logger
from tushare_integration.models.anns_d import AnnsD
from tushare_integration.models.cctv_news import CctvNews
from tushare_integration.models.major_news import MajorNews
from tushare_integration.models.ncov_global import NcovGlobal
from tushare_integration.models.ncov_num import NcovNum
from tushare_integration.models.news import News
from tushare_integration.spiders.tushare import LimitOffsetSpider, TimeSeriesSpider, TushareSpider

logger = get_logger()


class NewsSpider(LimitOffsetSpider):
    __model__: Type[News] = News

    def start_requests(self) -> Generator[httpx.Request, Any, Any]:
        """
        按小时进行数据采集。使用模型的 __start_date__ 作为起始时间，
        格式为 "YYYY-MM-DD HH:MM:SS"。每小时判断该时间段是否已有数据，
        如果有则跳过，否则调用采集接口采集数据。
        """

        # 检查 __start_date__ 是否定义，否则记录错误并返回
        if not hasattr(self.__model__, "__start_date__") or not self.__model__.__start_date__:
            logger.error("未定义 __start_date__，无法采集新闻数据")
            return

        dt = datetime.strptime(self.__model__.__start_date__, "%Y-%m-%d %H:%M:%S")
        # 获取当前小时的起始时间，确保结束时间不超过这个时间
        current_hour_start = datetime.now().replace(minute=0, second=0, microsecond=0)
        # 仅采集结束时间不超过当前小时起始时间（完整小时）的数据
        while dt + timedelta(hours=1) <= current_hour_start:
            hour_start = dt.strftime("%Y-%m-%d %H:%M:%S")
            hour_end = (dt + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

            # 检查该小时是否已有数据
            cnt = self.get_count(hour_start, hour_end)
            if cnt > 0:
                logger.debug(f"在 {hour_start} 到 {hour_end} 已有数据，跳过采集")
            else:
                logger.debug(f"在 {hour_start} 到 {hour_end} 无数据，开始采集")
                params = {"start_date": hour_start, "end_date": hour_end}
                yield self.get_httpx_request(params)
            dt += timedelta(hours=1)

    def get_count(self, start_date: str, end_date: str) -> int:
        """
        判断指定时间段内是否已有数据。此处假设模型提供 query_count 方法支持按时间段查询。
        """
        with self.db_engine.session() as session:
            stmt = select(func.count()).where(
                and_(
                    self.__model__.datetime >= start_date,
                    self.__model__.datetime < end_date,
                )
            )
            return session.execute(stmt).scalar_one()


class MajorNewsSpider(NewsSpider):
    __model__: Type[MajorNews] = MajorNews


class CctvNewsSpider(TimeSeriesSpider):
    __model__: Type[CctvNews] = CctvNews
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('D'):
            yield request


class AnnsDSpider(TimeSeriesSpider):
    __model__: Type[AnnsD] = AnnsD
    __trade_date_field__: str = 'date'

    def start_requests(self):
        for request in self.get_dates('D'):
            yield request


class NcovNumSpider(LimitOffsetSpider):
    __model__: Type[NcovNum] = NcovNum
    __limit__: int = 2000


class NcovGlobalSpider(LimitOffsetSpider):
    __model__: Type[NcovGlobal] = NcovGlobal
    __limit__: int = 10000
