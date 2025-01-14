from abc import ABC, abstractmethod
from typing import Any

from tushare_integration.crawler.settings import CrawlerSettings


class Pipeline(ABC):
    """
    管道基类，用于处理爬取到的数据
    """

    def __init__(self, settings: CrawlerSettings):
        self.settings = settings

    @abstractmethod
    def process_item(self, item: Any) -> Any:
        """处理数据项"""
        pass
