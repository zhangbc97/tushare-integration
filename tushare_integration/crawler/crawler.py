import logging
from typing import Dict, List, Type

from .settings import CrawlerSettings
from .spider import Spider


class Crawler:
    """
    爬虫管理器，负责管理组件和资源
    """

    def __init__(
        self,
        settings: CrawlerSettings,
        spider_classes: List[Type[Spider]],
    ):
        self.settings = settings
        self.spider_classes = spider_classes
        self.logger = logging.getLogger(self.__class__.__name__)
        self.spiders: Dict[str, Spider] = {}

    def create_spider(self, spider_cls: Type[Spider]) -> Spider:
        """创建一个新的spider实例"""
        middlewares = [middleware_cls(self.settings) for middleware_cls in self.settings.middlewares]
        pipelines = [pipeline_cls(self.settings) for pipeline_cls in self.settings.pipelines]
        return spider_cls(settings=self.settings, middlewares=middlewares, pipelines=pipelines, logger=self.logger)

    def start_spider(self, spider_name: str) -> None:
        """启动指定的爬虫

        Args:
            spider_name: 爬虫名称
        """
        # 查找对应的spider类
        spider_cls = next((cls for cls in self.spider_classes if cls.name == spider_name), None)
        if not spider_cls:
            raise ValueError(f"未找到爬虫: {spider_name}")

        # 创建并启动spider
        spider = self.create_spider(spider_cls)
        self.spiders[spider_name] = spider

        try:
            spider.run()
        except Exception as e:
            self.logger.error(f"爬虫 {spider_name} 运行出错: {e}")
            raise
        finally:
            # 运行结束后从字典中移除
            self.spiders.pop(spider_name, None)

    def start(self) -> None:
        """启动所有爬虫"""
        for spider_cls in self.spider_classes:
            self.start_spider(spider_cls.name)

    def stop_spider(self, spider_name: str) -> None:
        """停止指定的爬虫

        Args:
            spider_name: 爬虫名称
        """
        if spider := self.spiders.get(spider_name):
            spider.client.close()
            self.spiders.pop(spider_name)

    def stop(self) -> None:
        """停止所有爬虫"""
        for spider_name in list(self.spiders.keys()):
            self.stop_spider(spider_name)
