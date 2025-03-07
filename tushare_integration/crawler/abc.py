from abc import ABC, abstractmethod
from typing import ClassVar, Generator, Iterator

import httpx
import pandas as pd
from tushare_models.core.base import Base


class BaseSpider(ABC):
    """爬虫抽象基类"""

    __model__: ClassVar[type[Base]] = Base  # 数据模型类
    __spider_name__: str = ""  # 爬虫名称

    @abstractmethod
    def schedule_request(self, request: httpx.Request, first: bool = False) -> None:
        """调度请求到队列"""
        pass

    @abstractmethod
    def start_requests(self) -> Iterator[httpx.Request]:
        """生成初始请求"""
        pass

    @abstractmethod
    def parse(self, response: httpx.Response) -> Generator[pd.DataFrame, None, None]:
        """解析响应"""
        pass

    @abstractmethod
    def close(self) -> None:
        """关闭爬虫，清理资源"""
        pass
