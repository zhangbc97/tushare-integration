import threading
import time
from abc import ABC, abstractmethod
from typing import List, Set

import httpx

from tushare_integration.crawler.abc import BaseSpider
from tushare_integration.crawler.exception import RetryException
from tushare_integration.logger import get_logger
from tushare_integration.settings import TushareIntegrationSettings


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

    # 可重试的API错误码
    RETRY_API_CODES: List[int] = [
        40201,  # API调用次数超限
        # 可在此处添加其他需要重试的错误码
    ]

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self.logger = get_logger()
        self._lock = threading.RLock()  # 添加可重入锁

    def process_request(self, request: httpx.Request) -> httpx.Request:
        """处理请求"""
        return request

    def process_response(self, response: httpx.Response) -> httpx.Response:
        """处理响应，对指定的API错误码进行重试

        Args:
            response: 响应对象

        Returns:
            处理后的响应对象

        """
        data = response.json()
        code = data.get("code", 0)

        # 检查是否是可重试的API错误码
        if code in self.RETRY_API_CODES:
            with self._lock:  # 使用锁保护重试逻辑
                request = response.request
                retry_count = request.extensions.get("retry_count", 0)

                if retry_count < self.settings.retry_times:
                    request.extensions["retry_count"] = retry_count + 1
                    retry_msg = "API error code %d - %s" % (code, data.get('msg', 'Unknown error'))

                    self.logger.warning(
                        "Request failed (attempt %d/%d): %s\n" "URL: %s\n" "Method: %s\n" "Will retry in %d seconds",
                        retry_count + 1,
                        self.settings.retry_times,
                        retry_msg,
                        request.url,
                        request.method,
                        self.settings.retry_delay,
                    )

                    time.sleep(self.settings.retry_delay)
                    
                    raise RetryException(retry_msg)
                else:
                    raise Exception(
                        "Request failed after %d retries: %s" % (retry_count, data.get('msg', 'Unknown error'))
                    )
        elif code != 0:
            raise Exception(
                "Request failed with non-retryable error code %d: %s" % (code, data.get('msg', 'Unknown error'))
            )

        return response

    def process_exception(self, request: httpx.Request, exception: Exception) -> None:
        """处理异常，对于网络错误进行重试

        Args:
            request: 请求对象
            exception: 异常对象
        """
        if isinstance(exception, (httpx.NetworkError, httpx.TimeoutException, RetryException)):
            with self._lock:  # 使用锁保护异常重试逻辑
                retry_count = request.extensions.get("retry_count", 0)
                if retry_count < self.settings.retry_times:
                    request.extensions["retry_count"] = retry_count + 1

                    self.logger.warning(
                        "Network error (attempt %d/%d): %s\n" "URL: %s\n" "Method: %s\n" "Will retry in %d seconds",
                        retry_count + 1,
                        self.settings.retry_times,
                        str(exception),
                        request.url,
                        request.method,
                        self.settings.retry_delay,
                    )

                    time.sleep(self.settings.retry_delay)
                    self.spider.schedule_request(request, first=True)
                else:
                    self.logger.error(
                        "Network error after %d retries: %s\n" "URL: %s\n" "Method: %s",
                        retry_count,
                        str(exception),
                        request.url,
                        request.method,
                    )
