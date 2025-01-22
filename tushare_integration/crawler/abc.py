from abc import ABC, abstractmethod
from typing import Any, ClassVar, Generator, Iterator

import httpx
import pandas as pd

from tushare_integration.models.core.base import Base
from tushare_integration.settings import TushareIntegrationSettings


class BaseSpider(ABC):
    """爬虫抽象基类"""

    __spider_name__: str = ""
    __model__: ClassVar[type[Base]] = Base  # 数据模型类

    @property
    @abstractmethod
    def settings(self) -> TushareIntegrationSettings:
        """获取爬虫配置"""
        pass

    @abstractmethod
    def schedule_request(self, request: httpx.Request, first: bool = False) -> None:
        """调度请求到队列

        Args:
            request: 要调度的请求
            first: 是否添加到队列头部，默认False（添加到队列尾部）
        """
        pass

    @abstractmethod
    def start_requests(self) -> Iterator[httpx.Request]:
        """生成初始请求"""
        pass

    @abstractmethod
    def parse(self, response: httpx.Response) -> Generator[pd.DataFrame, None, None]:
        """解析响应

        Args:
            response: 响应对象

        Returns:
            生成器，生成 DataFrame 数据
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭爬虫，清理资源

        在爬虫结束时调用，用于清理资源，如关闭网络连接等。
        """
        pass
