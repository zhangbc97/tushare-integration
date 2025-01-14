import logging
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Deque, Generator, Iterator, List, Optional

import httpx

from .middleware import Middleware
from .pipeline import Pipeline
from .settings import CrawlerSettings


class Spider(ABC):
    """
    爬虫基类，负责控制整个采集流程
    """

    name: str = ""

    def __init__(
        self,
        settings: CrawlerSettings,
        middlewares: List[Middleware],
        pipelines: List[Pipeline],
        logger: Optional[logging.Logger] = None,
    ):
        self.settings = settings
        self.client = httpx.Client(timeout=settings.timeout, headers=settings.headers)
        self.middlewares = middlewares
        self.pipelines = pipelines
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.request_queue: Deque[httpx.Request] = deque()

    def schedule_request(self, request: httpx.Request, to_front: bool = False) -> None:
        """将请求加入队列

        Args:
            request: 要调度的请求
            to_front: 是否插入到队列头部。重试请求应该插入到队头以保持顺序。
        """
        if to_front:
            self.request_queue.appendleft(request)
        else:
            self.request_queue.append(request)

    def next_request(self) -> httpx.Request:
        """获取下一个要处理的请求

        Returns:
            下一个要处理的请求

        Raises:
            IndexError: 当队列为空时抛出,表示爬虫应该结束
        """
        return self.request_queue.popleft()

    def process_request(self, request: httpx.Request) -> Optional[httpx.Response]:
        """处理请求

        Returns:
            - httpx.Response: 成功获取到响应
            - None: 请求被重新调度
        """
        # 中间件处理请求
        for middleware in self.middlewares:
            try:
                result = middleware.process_request(request)
                if isinstance(result, httpx.Response):
                    # 如果返回响应,直接处理响应
                    return self.process_response(request, result)
                elif isinstance(result, httpx.Request):
                    request = result
            except Exception as e:
                # 处理异常
                result = self.process_exception(request, e)
                if result:
                    if isinstance(result, httpx.Request):
                        self.schedule_request(result, to_front=True)  # 重试请求插入队头
                        return None
                    return result
                raise

        # 发送请求
        try:
            response = self.client.send(request)
        except Exception as e:
            result = self.process_exception(request, e)
            if result:
                if isinstance(result, httpx.Request):
                    self.schedule_request(result, to_front=True)  # 重试请求插入队头
                    return None
                return result
            raise

        return self.process_response(request, response)

    def process_response(self, request: httpx.Request, response: httpx.Response) -> Optional[httpx.Response]:
        """处理响应

        Returns:
            - httpx.Response: 处理后的响应
            - None: 请求被重新调度
        """
        for middleware in self.middlewares:
            try:
                result = middleware.process_response(request, response)
                if isinstance(result, httpx.Request):
                    # 如果返回新请求,加入队列头部
                    self.schedule_request(result, to_front=True)  # 重试请求插入队头
                    return None
                response = result
            except Exception as e:
                result = self.process_exception(request, e)
                if result:
                    if isinstance(result, httpx.Request):
                        self.schedule_request(result, to_front=True)  # 重试请求插入队头
                        return None
                    return result
                raise
        return response

    def process_exception(self, request: httpx.Request, exception: Exception) -> Optional[httpx.Response]:
        """处理异常

        Args:
            request: 发生异常的请求
            exception: 异常对象

        Returns:
            Optional[httpx.Response]: 如果异常被处理则返回响应,否则返回None
        """
        for middleware in self.middlewares:
            try:
                result = middleware.process_exception(request, exception)
                if result:
                    if isinstance(result, httpx.Request):
                        self.schedule_request(result, to_front=True)  # 重试请求插入队头
                        return None
                    return result
            except Exception as e:
                exception = e
        return None

    def process_item(self, item: Any) -> Any:
        """处理数据项"""
        for pipeline in self.pipelines:
            item = pipeline.process_item(item)
        return item

    def run(self):
        """运行爬虫"""
        try:
            # 初始化请求队列
            for request in self.start_requests():
                self.schedule_request(request)

            # 处理队列中的请求
            try:
                while request := self.next_request():
                    response = self.process_request(request)
                    if response:
                        for item in self.parse(response):
                            self.process_item(item)
            except IndexError:
                # 队列为空,爬虫结束
                pass
        finally:
            self.client.close()

    @abstractmethod
    def start_requests(self) -> Iterator[httpx.Request]:
        """生成初始请求"""
        raise NotImplementedError

    @abstractmethod
    def parse(self, response: httpx.Response) -> Generator[Any, None, None]:
        """解析响应"""
        raise NotImplementedError
