import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional, Union

import httpx

from .settings import CrawlerSettings


class Middleware(ABC):
    """
    中间件基类

    中间件用于处理请求和响应:
    - process_request 可以修改请求、直接返回响应或抛出异常
    - process_response 可以修改响应、返回新的请求或抛出异常
    - process_exception 可以处理异常、返回响应或新的请求
    """

    def __init__(self, settings: CrawlerSettings):
        self.settings = settings

    @abstractmethod
    def process_request(self, request: httpx.Request) -> Optional[Union[httpx.Request, httpx.Response]]:
        """处理请求

        Args:
            request: 原始请求

        Returns:
            - None: 继续处理请求
            - httpx.Request: 使用新的请求替换原始请求
            - httpx.Response: 直接返回响应,跳过后续中间件

        Raises:
            Exception: 触发异常处理流程
        """
        pass

    @abstractmethod
    def process_response(
        self, request: httpx.Request, response: httpx.Response
    ) -> Union[httpx.Response, httpx.Request]:
        """处理响应

        Args:
            request: 原始请求
            response: 原始响应

        Returns:
            - httpx.Response: 返回处理后的响应
            - httpx.Request: 返回新的请求,将重新调度该请求

        Raises:
            Exception: 触发异常处理流程
        """
        return response

    @abstractmethod
    def process_exception(
        self, request: httpx.Request, exception: Exception
    ) -> Optional[Union[httpx.Response, httpx.Request]]:
        """处理异常

        Args:
            request: 发生异常的请求
            exception: 异常对象

        Returns:
            - None: 继续异常处理流程
            - httpx.Response: 返回响应,终止异常处理
            - httpx.Request: 返回新的请求,将重新调度该请求
        """
        pass


class ThrottleMiddleware(Middleware):
    """
    限流中间件

    通过控制请求间隔来限制请求速率。
    当达到限流阈值或收到限流响应时，会自动等待后重试请求。
    """

    def __init__(self, settings: CrawlerSettings):
        super().__init__(settings)
        self.last_request_time = 0.0
        self.delay = 1.0 / settings.concurrent_requests  # 根据并发数计算延迟

    def process_request(self, request: httpx.Request) -> Optional[Union[httpx.Request, httpx.Response]]:
        """处理请求，控制请求间隔"""
        now = time.time()
        if self.last_request_time:
            wait = self.delay - (now - self.last_request_time)
            if wait > 0:
                logging.debug(f"请求频率过高，等待 {wait:.2f} 秒")
                time.sleep(wait)

        self.last_request_time = time.time()
        return request

    def process_response(
        self, request: httpx.Request, response: httpx.Response
    ) -> Union[httpx.Response, httpx.Request]:
        """处理响应，检查是否出现限流"""
        try:
            resp_data = response.json()
            # 检查是否是限流错误(402XX)
            if resp_data.get("code", 0) // 100 == 402:
                logging.warning(
                    f"触发限流保护，等待 {self.settings.retry_delay} 秒后重试。错误码: {resp_data.get('code')}"
                )
                time.sleep(self.settings.retry_delay)
                return request  # 返回原始请求以重试
        except json.JSONDecodeError:
            logging.warning(f"响应解析失败: {response.text[:100]}")
            pass

        return response

    def process_exception(
        self, request: httpx.Request, exception: Exception
    ) -> Optional[Union[httpx.Response, httpx.Request]]:
        """处理异常"""
        return None
