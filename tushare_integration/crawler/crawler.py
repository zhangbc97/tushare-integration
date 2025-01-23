import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from graphlib import TopologicalSorter
from typing import Dict, List, Set, Type

from tushare_integration.crawler.spider import Spider, SpiderMeta
from tushare_integration.settings import TushareIntegrationSettings


class Crawler(object):
    """爬虫运行时环境,负责管理爬虫的生命周期"""

    def __init__(self, settings: TushareIntegrationSettings) -> None:
        """初始化爬虫运行时环境

        Args:
            settings: 配置对象
        """
        self.settings = settings
        self._running_spiders: List[Spider] = []
        self.max_workers = settings.concurrent_spiders
        self._lock = threading.Lock()

    def _build_dependency_graph(self, pattern: str) -> tuple[Dict[str, Set[str]], Dict[str, Type[Spider]]]:
        """构建依赖图

        Args:
            pattern: Spider名称匹配模式

        Returns:
            tuple: (依赖关系字典, spider类字典)
                - 依赖关系字典: {spider_name -> {dependency_names}}
                - spider类字典: {spider_name -> spider_class}
        """
        # 获取匹配的爬虫和依赖图
        graph = {}
        spider_classes = {}  # name -> class 映射

        # 收集匹配的爬虫
        for spider_name, spider_class in SpiderMeta.get_all_spiders().items():
            if re.match(pattern, spider_name):
                spider_classes[spider_name] = spider_class
                graph[spider_name] = set()

        # 添加依赖关系
        for spider_name, spider_class in spider_classes.items():
            if hasattr(spider_class.__model__, '__dependencies__'):
                for dep_name in spider_class.__model__.__dependencies__:
                    dep_class = SpiderMeta.get(dep_name)
                    if dep_class is None:
                        raise ValueError(f"找不到依赖的爬虫: {dep_name}")
                    # 确保依赖的爬虫也在图中
                    if dep_name not in graph:
                        graph[dep_name] = set()
                        spider_classes[dep_name] = dep_class
                    # 添加依赖关系
                    graph[spider_name].add(dep_name)

        return graph, spider_classes

    def crawl(self, pattern: str) -> None:
        """并发运行爬虫

        Args:
            pattern: 爬虫名称匹配模式
        """
        # 构建依赖图
        graph, spider_classes = self._build_dependency_graph(pattern)
        if not graph:
            return

        # 创建拓扑排序器
        sorter = TopologicalSorter(graph)
        sorter.prepare()

        # 使用线程池执行任务
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 跟踪运行中的任务
            running_tasks = {}  # future -> spider_name 映射

            while sorter.is_active():
                # 提交新的准备好的任务
                for spider_name in sorter.get_ready():
                    spider_class = spider_classes[spider_name]
                    future = executor.submit(self._run_spider, spider_class)
                    running_tasks[future] = spider_name

                # 等待任意任务完成
                if running_tasks:
                    # 等待最早完成的任务
                    done, _ = next(as_completed(running_tasks)), None
                    spider_name = running_tasks.pop(done)
                    try:
                        done.result()  # 检查是否有异常
                        sorter.done(spider_name)  # 标记任务完成
                    except Exception:
                        self.stop()
                        raise

    def _run_spider(self, spider_class: Type[Spider]) -> None:
        """运行单个爬虫"""
        spider = spider_class(self.settings)
        with self._lock:
            self._running_spiders.append(spider)
        try:
            spider.start()
        finally:
            with self._lock:
                spider.close()
                self._running_spiders.remove(spider)

    def stop(self) -> None:
        """停止所有运行中的爬虫"""
        with self._lock:
            for spider in self._running_spiders:
                spider.close()
            self._running_spiders.clear()
