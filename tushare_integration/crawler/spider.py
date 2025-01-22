from abc import abstractmethod
from collections import deque
from typing import ClassVar, Deque, Generator, Iterator, List, Optional, Type

import httpx
import pandas as pd

from tushare_integration.crawler.abc import BaseSpider
from tushare_integration.crawler.middleware import Middleware, RetryMiddleware, ThrottleMiddleware
from tushare_integration.crawler.pipeline import (
    DataPipeline,
    FillNAPipeline,
    Pipeline,
    RecordLogPipeline,
    TransformDTypePipeline,
)
from tushare_integration.models.core.base import Base
from tushare_integration.settings import TushareIntegrationSettings


class Spider(BaseSpider):
    """爬虫实现类"""

    __spider_name__: str = ""
    __model__: ClassVar[type[Base]] = Base  # 数据模型类
    middleware_classes: List[Type[Middleware]] = [
        RetryMiddleware,
        ThrottleMiddleware,
    ]  # 默认启用重试和限流中间件
    pipeline_classes: List[Type[Pipeline]] = [  # 默认启用的管道
        FillNAPipeline,
        TransformDTypePipeline,
        DataPipeline,
        RecordLogPipeline,
    ]

    def __init__(self, settings: TushareIntegrationSettings):
        self._settings = settings
        self.client = httpx.Client(
            timeout=settings.timeout,
            headers=settings.headers,
        )
        self._request_queue: Deque[httpx.Request] = deque()

        # 初始化中间件
        self.middlewares = [
            middleware_cls(settings=settings, spider=self) for middleware_cls in self.middleware_classes
        ]

        # 初始化管道
        self.pipelines = [pipeline_cls(settings=settings, spider=self) for pipeline_cls in self.pipeline_classes]

    @property
    def settings(self) -> TushareIntegrationSettings:
        return self._settings

    def start(self) -> None:
        """启动爬虫"""
        try:
            # 初始化请求队列
            for request in self.start_requests():
                self.schedule_request(request)

            # 处理队列中的请求直到队列为空
            while self._request_queue:
                request = self._request_queue.popleft()
                if response := self._process_request(request):
                    self._process_data(response)
        finally:
            self.close()

    def schedule_request(self, request: httpx.Request, first: bool = False) -> None:
        """调度请求到队列

        Args:
            request: 要调度的请求
            first: 是否添加到队列头部，默认False（添加到队列尾部）
        """
        if first:
            self._request_queue.appendleft(request)
        else:
            self._request_queue.append(request)

    def _process_request(self, request: httpx.Request) -> Optional[httpx.Response]:
        """处理请求并获取响应

        Args:
            request: 请求对象

        Returns:
            响应对象，如果请求处理失败则返回None
        """
        try:
            # 执行请求中间件
            for middleware in self.middlewares:
                request = middleware.process_request(request)

            # 发送请求
            response = self.client.send(request)

            # 执行响应中间件
            for middleware in self.middlewares:
                response = middleware.process_response(response)

            return response

        except Exception as e:
            for middleware in self.middlewares:
                middleware.process_exception(request, e)
            return None

    def _process_data(self, response: httpx.Response) -> None:
        """处理响应数据

        Args:
            response: 响应对象
        """
        try:
            # 解析响应并处理数据
            for item in self.parse(response):
                self._process_item(item)
        except Exception:
            # 数据处理异常不触发中间件
            raise

    def _process_item(self, item: pd.DataFrame) -> None:
        """处理数据项

        Args:
            item: 数据项(DataFrame)
        """
        processed_item: pd.DataFrame | None = item
        for pipeline in self.pipelines:
            processed_item = pipeline.process_item(processed_item)
            if processed_item is None:
                break

    @abstractmethod
    def start_requests(self) -> Iterator[httpx.Request]:
        """生成初始请求"""
        raise NotImplementedError

    @abstractmethod
    def parse(self, response: httpx.Response) -> Generator[pd.DataFrame, None, None]:
        """解析响应

        Args:
            response: 响应对象

        Returns:
            生成器，生成 DataFrame 数据
        """
        raise NotImplementedError

    def close(self) -> None:
        """关闭爬虫，清理资源"""
        self.client.close()
