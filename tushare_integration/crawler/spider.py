import json
import re
import threading
import time
from abc import ABCMeta, abstractmethod
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import ClassVar, Deque, Dict, Generator, Iterator, List, Type, cast

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
from tushare_integration.dictionary import API_PATH_DICTIONARY
from tushare_integration.logger import get_logger
from tushare_integration.models.core.base import Base
from tushare_integration.settings import TushareIntegrationSettings

logger = get_logger()


class SpiderMeta(ABCMeta):
    """Spider元类,用于注册爬虫类

    继承ABCMeta以支持抽象基类,同时实现Spider注册功能
    """

    _registry: Dict[str, Type["Spider"]] = {}

    def __new__(mcs, name: str, bases: tuple, attrs: dict):
        # 创建类
        cls = super().__new__(mcs, name, bases, attrs)

        # 获取spider_name，在__model__中的__api_name__
        model = attrs.get('__model__', {})

        if not hasattr(model, '__api_name__'):
            return cls

        spider_name = model.__api_name__

        # 只注册非空spider_name的爬虫类,且不注册基类Spider
        if spider_name:
            if spider_name in mcs._registry:
                raise ValueError(f'重复的爬虫名称: {spider_name}')
            # 设置类的 __spider_name__ 属性
            setattr(cls, '__spider_name__', spider_name)
            mcs._registry[spider_name] = cast(Type["Spider"], cls)

        return cls

    @classmethod
    def get_all_spiders(cls) -> Dict[str, Type["Spider"]]:
        """获取所有注册的爬虫类"""
        return cls._registry.copy()

    @classmethod
    def get(cls, spider_name: str) -> Type["Spider"]:
        """获取指定名称的爬虫类"""
        if spider := cls._registry.get(spider_name):
            return spider
        raise ValueError(f"未找到爬虫: {spider_name}")

    @classmethod
    def list_spiders(cls, pattern: str | None = None) -> List[Type['Spider']]:
        """列出所有爬虫或匹配模式的爬虫

        Args:
            pattern: 匹配模式，可以是爬虫名称模式或路径模式。
                    如果包含'/'，则按路径匹配；否则按名称匹配。
                    不传则返回所有爬虫。

        Returns:
            List[Type['Spider']]: 爬虫类列表
        """
        if pattern is None:
            return list(cls._registry.values())

        if '/' in pattern:
            return cls._list_spiders_by_path(pattern)

        matched_spiders = []
        for spider_class in cls._registry.values():
            if re.fullmatch(pattern, spider_class.__spider_name__):
                matched_spiders.append(spider_class)
        return matched_spiders

    @classmethod
    def _list_spiders_by_path(cls, path_pattern: str) -> List[Type["Spider"]]:
        """通过API路径模式匹配爬虫

        Args:
            path_pattern: API路径匹配模式，如 'stock/basic'

        Returns:
            匹配的爬虫类列表
        """
        path_parts = path_pattern.strip('/').split('/')

        matched_spiders = []
        for spider_name, spider_cls in cls._registry.items():
            model = getattr(spider_cls, '__model__', None)
            if not (model and hasattr(model, '__api_path__')):
                continue

            api_path = [API_PATH_DICTIONARY.get(part, part) for part in model.__api_path__[:-1]]
            # 添加最后一个元素，使用__api_name__
            api_path.append(getattr(model, '__api_name__', model.__api_path__[-1]))
            # 跳过第一个元素进行匹配
            match = True
            for i, pattern in enumerate(path_parts):
                # 直接从第二个元素开始匹配
                api_path_index = i + 1
                if api_path_index >= len(api_path):
                    match = False
                    break
                if not re.fullmatch(pattern, api_path[api_path_index]):
                    match = False
                    break

            if match:
                matched_spiders.append(spider_cls)

        return matched_spiders


class Spider(BaseSpider, metaclass=SpiderMeta):
    """爬虫实现类

    警告:
        不要轻易将此类改为多线程实现，除非能确保所有的middleware和pipeline都是线程安全的。
        当前的middleware和pipeline可能存在线程安全问题，贸然使用多线程可能导致数据不一致或竞态条件。
    """

    __model__: ClassVar[type[Base]] = Base
    middleware_classes: List[Type[Middleware]] = [
        RetryMiddleware,
        ThrottleMiddleware,
    ]
    pipeline_classes: List[Type[Pipeline]] = [
        FillNAPipeline,
        TransformDTypePipeline,
        DataPipeline,
        RecordLogPipeline,
    ]

    def __init__(self, settings: TushareIntegrationSettings):
        self.settings = settings

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

        # 添加运行状态控制
        self._running = False
        self._lock = threading.RLock()

    def start(self) -> None:
        """启动爬虫"""
        with self._lock:
            if self._running:
                logger.warning("Spider %s is already running", self.__spider_name__)
                return
            self._running = True

        try:
            logger.debug("Spider %s initializing request queue", self.__spider_name__)
            for request in self.start_requests():
                self.schedule_request(request)

            logger.debug("Spider %s has %d requests queued", self.__spider_name__, len(self._request_queue))

            with ThreadPoolExecutor(max_workers=self.settings.max_workers_per_spider) as executor:
                # 启动所有线程并等待执行完毕
                futures = [executor.submit(self._worker) for _ in range(self.settings.max_workers_per_spider)]
                for _ in as_completed(futures):
                    pass
        except Exception as e:
            logger.exception("Spider %s encountered error: %s", self.__spider_name__, str(e))
            raise
        finally:
            self.close()

    def _worker(self) -> None:
        while self._request_queue and self._running:
            request = self._request_queue.popleft()
            if response := self._process_request(request):
                logger.debug("Spider %s got response, processing data", self.__spider_name__)
                self._process_data(response)
            else:
                logger.warning("Spider %s got no response for request", self.__spider_name__)

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

    def _process_request(self, request: httpx.Request) -> httpx.Response | None:
        """请求并获取响应

        Args:
            request: 请求对象

        Returns:
            响应对象，如果请求失败则返回None
        """
        try:
            # 执行请求中间件
            for middleware in self.middlewares:
                request = middleware.process_request(request)

            # 修改日志输出格式
            logger.info("Request %s with params: %s", self.__spider_name__, json.loads(request.content)['params'])
            # 发送请求
            response: httpx.Response = self.client.send(request)

            # 执行响应中间件
            for middleware in self.middlewares:
                response = middleware.process_response(response)

            return response

        except Exception as e:
            for middleware in self.middlewares:
                middleware.process_exception(request, e)

    def _process_data(self, response: httpx.Response) -> None:
        """处理响应数据"""
        try:
            logger.debug("Spider %s parsing response", self.__spider_name__)
            # 解析响应并处理数据
            for item in self.parse(response):
                if not isinstance(item, pd.DataFrame):
                    raise TypeError(
                        "Spider %s parse() method returned %s, expected pandas.DataFrame",
                        self.__spider_name__,
                        type(item),
                    )

                logger.debug("Spider %s processing item with shape %s", self.__spider_name__, item.shape)
                self._process_item(item)
            logger.debug("Spider %s finished processing response", self.__spider_name__)
        except Exception as e:
            logger.exception("Spider %s failed to process data: %s", self.__spider_name__, str(e))
            raise

    def _process_item(self, item: pd.DataFrame) -> None:
        """处理数据项"""
        processed_item: pd.DataFrame | None = item
        for pipeline in self.pipelines:
            logger.debug("Spider %s running pipeline %s", self.__spider_name__, pipeline.__class__.__name__)
            processed_item = pipeline.process_item(processed_item)
            if processed_item is None:
                logger.debug("Pipeline %s dropped item", pipeline.__class__.__name__)
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
        with self._lock:
            if not self._running:  # 如果未运行，直接返回
                return
            self._running = False

            logger.debug("Spider %s closing...", self.__spider_name__)
            self._request_queue.clear()

            # 关闭所有pipeline
            for pipeline in self.pipelines:
                pipeline.close()

            self.client.close()
            logger.debug("Spider %s closed", self.__spider_name__)

    def __hash__(self) -> int:
        """使用spider_name作为哈希值"""
        return hash(self.__spider_name__)

    def __eq__(self, other: object) -> bool:
        """通过spider_name判断相等性"""
        if not isinstance(other, Spider):
            return NotImplemented
        return self.__spider_name__ == other.__spider_name__

    def __repr__(self) -> str:
        """返回spider的字符串表示"""
        return f"<Spider {self.__spider_name__}>"
