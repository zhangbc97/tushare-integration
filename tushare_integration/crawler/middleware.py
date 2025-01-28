import threading
import time
from abc import ABC, abstractmethod
from typing import Set

import httpx

from tushare_integration.crawler.abc import BaseSpider
from tushare_integration.settings import TushareIntegrationSettings
from tushare_integration.logger import get_logger


class Middleware(ABC):
    """中间件基类"""

    __spider_name__: str

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        """初始化中间件

        Args:
            settings: 配置对象
            spider: 爬虫实例
        """
        self.settings = settings
        self.spider = spider

    @abstractmethod
    def process_request(self, request: httpx.Request) -> httpx.Request:
        """处理请求

        Args:
            request: 请求对象

        Returns:
            处理后的请求对象

        Raises:
            Exception: 如果需要中断请求处理
        """
        pass

    @abstractmethod
    def process_response(self, response: httpx.Response) -> httpx.Response:
        """处理响应

        Args:
            response: 响应对象

        Returns:
            处理后的响应对象

        Raises:
            Exception: 如果需要中断响应处理
        """
        pass

    @abstractmethod
    def process_exception(self, request: httpx.Request, exception: Exception) -> None:
        """处理异常

        Args:
            request: 请求对象
            exception: 异常对象
        """
        pass


class ThrottleMiddleware(Middleware):
    """限流中间件"""

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self._last_request_time: float = 0
        self._min_interval: float = 60.0 / settings.max_requests_per_minute  # 计算最小请求间隔
        self._lock = threading.RLock()  # 使用可重入锁

    def process_request(self, request: httpx.Request) -> httpx.Request:
        """实现请求频率限制

        Args:
            request: 请求对象

        Returns:
            处理后的请求对象
        """
        with self._lock:  # 使用锁保护临界区
            now = time.time()
            wait = self._min_interval - (now - self._last_request_time)
            if wait > 0:
                time.sleep(wait)
            self._last_request_time = time.time()
            return request

    def process_response(self, response: httpx.Response) -> httpx.Response:
        """处理响应"""
        return response

    def process_exception(self, request: httpx.Request, exception: Exception) -> None:
        """处理异常"""
        pass


class RetryMiddleware(Middleware):
    """重试中间件"""

    # 可重试的HTTP状态码
    RETRY_HTTP_STATUS_CODES: Set[int] = {
        408,  # Request Timeout
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
    }

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self.logger = get_logger()

    def process_request(self, request: httpx.Request) -> httpx.Request:
        """处理请求"""
        return request

    def process_response(self, response: httpx.Response) -> httpx.Response:
        """处理响应，只对 402XX 错误码进行重试

        Args:
            response: 响应对象

        Returns:
            处理后的响应对象

        Raises:
            Exception: 如果需要重试则抛出异常
        """
        try:
            data = response.json()
            code = data.get("code", 0)

            # 检查是否是 402XX 错误码
            if 40200 <= code < 40300:
                request = response.request
                retry_count = request.extensions.get("retry_count", 0)

                if retry_count < self.settings.retry_times:
                    request.extensions["retry_count"] = retry_count + 1
                    retry_msg = f"API error code {code} - {data.get('msg', 'Unknown error')}"

                    self.logger.warning(
                        f"Request failed (attempt {retry_count + 1}/{self.settings.retry_times}): {retry_msg}\n"
                        f"URL: {request.url}\n"
                        f"Method: {request.method}\n"
                        f"Will retry in {self.settings.retry_delay} seconds"
                    )

                    # 等待指定时间后重试
                    time.sleep(self.settings.retry_delay)
                    # 将请求重新加入队列
                    self.spider.schedule_request(request, first=True)
                    raise Exception(f"Retrying {request.url} ({retry_msg}, attempt {retry_count + 1})")
                else:
                    self.logger.error(
                        f"Request failed after {retry_count} retries: {data.get('msg', 'Unknown error')}\n"
                        f"URL: {request.url}\n"
                        f"Method: {request.method}\n"
                        f"Error Code: {code}"
                    )
            elif code != 0:
                # 非 402XX 的错误码，记录错误但不重试
                self.logger.error(
                    f"Request failed with non-retryable error code {code}: {data.get('msg', 'Unknown error')}\n"
                    f"URL: {response.request.url}\n"
                    f"Method: {response.request.method}"
                )

        except ValueError:
            # JSON 解析失败，检查 HTTP 状态码
            if response.status_code in self.RETRY_HTTP_STATUS_CODES:
                self.logger.warning(
                    f"Request failed with HTTP status {response.status_code}\n"
                    f"URL: {response.request.url}\n"
                    f"Method: {response.request.method}"
                )

        return response

    def process_exception(self, request: httpx.Request, exception: Exception) -> None:
        """处理异常，对于网络错误进行重试

        Args:
            request: 请求对象
            exception: 异常对象
        """
        if isinstance(exception, (httpx.NetworkError, httpx.TimeoutException)):
            retry_count = request.extensions.get("retry_count", 0)
            if retry_count < self.settings.retry_times:
                request.extensions["retry_count"] = retry_count + 1

                self.logger.warning(
                    f"Network error (attempt {retry_count + 1}/{self.settings.retry_times}): {str(exception)}\n"
                    f"URL: {request.url}\n"
                    f"Method: {request.method}\n"
                    f"Will retry in {self.settings.retry_delay} seconds"
                )

                # 等待指定时间后重试
                time.sleep(self.settings.retry_delay)
                # 将请求重新加入队列
                self.spider.schedule_request(request, first=True)
            else:
                self.logger.error(
                    f"Network error after {retry_count} retries: {str(exception)}\n"
                    f"URL: {request.url}\n"
                    f"Method: {request.method}"
                )
