import threading
import time
from abc import ABC, abstractmethod
from typing import Set

import httpx

from tushare_integration.crawler.abc import BaseSpider
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

    def __init__(self, settings: TushareIntegrationSettings, spider: BaseSpider):
        super().__init__(settings, spider)
        self.logger = get_logger()
        self._lock = threading.RLock()  # 添加可重入锁

    def process_request(self, request: httpx.Request) -> httpx.Request:
        """处理请求"""
        return request

    def process_response(self, response: httpx.Response) -> httpx.Response:
        """处理响应，只对 402XX 错误码进行重试

        Args:
            response: 响应对象

        Returns:
            处理后的响应对象

        """
        data = response.json()

        with self._lock:
            if (code := data.get("code", 0)) == 0:
                return response
            # 检查是否是 402XX 错误码，如果是则重试
            elif 40200 <= code < 40300:
                request = response.request
                retry_count = request.extensions.get("retry_count", 0)

                if retry_count < self.settings.retry_times:
                    request.extensions["retry_count"] = retry_count + 1
                    retry_msg = "API error code %d - %s" % (code, data.get('msg', 'Unknown error'))

                    self.logger.warning(
                        "Request RateLimit (attempt %d/%d): %s\n" "URL: %s\n" "Method: %s\n" "Will retry in %d seconds",
                        retry_count + 1,
                        self.settings.retry_times,
                        retry_msg,
                        request.url,
                        request.method,
                        self.settings.retry_delay,
                    )

                    time.sleep(self.settings.retry_delay)
                    self.spider.schedule_request(request, first=True)
                    # 这里抛异常不会中断Spider的流程，如果不抛的话会导致后续解析报错，中断Spider的流程
                    raise Exception("Retrying %s (%s, attempt %d)", request.url, retry_msg, retry_count + 1)
                else:
                    self.logger.error(
                        "Request RateLimit after %d retries: %s\n" "URL: %s\n" "Method: %s\n" "Error Code: %d",
                        retry_count,
                        data.get('msg', 'Unknown error'),
                        request.url,
                        request.method,
                        code,
                    )
                    # 异常只在上面抛出，这里不抛，直接在解析阶段报错即可
            else:
                self.logger.error(
                    "Request failed with non-retryable error code %d: %s\n" "URL: %s\n" "Method: %s",
                    code,
                    data.get('msg', 'Unknown error'),
                    response.request.url,
                    response.request.method,
                )
                # 异常只在上面抛出，这里不抛，直接在解析阶段报错即可

        return response

    def process_exception(self, request: httpx.Request, exception: Exception) -> None:
        """处理异常，对于网络错误进行重试

        Args:
            request: 请求对象
            exception: 异常对象
        """
        if isinstance(exception, (httpx.NetworkError, httpx.TimeoutException)):
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
                    # 这里抛出异常直接中断Spider的流程
                    raise exception
