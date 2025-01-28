import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from graphlib import TopologicalSorter
from typing import Any, Dict, List, Set, Type

from tushare_integration.crawler.spider import Spider, SpiderMeta
from tushare_integration.logger import get_logger
from tushare_integration.settings import TushareIntegrationSettings

logger = get_logger()


class Crawler(object):
    """爬虫运行时环境,负责管理爬虫的生命周期"""

    def __init__(self, settings: TushareIntegrationSettings) -> None:
        """初始化爬虫运行时环境

        Args:
            settings: 配置对象
        """
        self.settings = settings
        logger.info("Initializing crawler...")
        self.max_workers = settings.concurrent_spiders
        self._lock = threading.Lock()
        self._running_spiders: List[Spider] = []
        self._results: List[Dict[str, Any]] = []
        self._running = True

    def _build_dependency_graph(self, pattern: str) -> Dict[str, Set[str]]:
        """构建依赖图

        Args:
            pattern: Spider名称匹配模式

        Returns:
            Dict[str, Set[str]]: 依赖关系字典 {spider_name -> {dependency_names}}
        """
        # 获取匹配的爬虫和依赖图
        graph = {}

        # 收集匹配的爬虫
        for spider_name, spider_class in SpiderMeta.get_all_spiders().items():
            if re.match(pattern, spider_name):
                graph[spider_name] = set()
                logger.info(f"Found matching spider: {spider_name}")

        # 添加依赖关系
        for spider_name in list(graph.keys()):
            spider_class = SpiderMeta.get(spider_name)
            if hasattr(spider_class.__model__, '__dependencies__'):
                deps = spider_class.__model__.__dependencies__
                logger.debug(f"Dependencies for spider {spider_name}: {deps}")
                for dep_name in deps:
                    dep_class = SpiderMeta.get(dep_name)
                    if dep_class is None:
                        raise ValueError(f"Dependent spider not found: {dep_name}")
                    # 确保依赖的爬虫也在图中
                    if dep_name not in graph:
                        graph[dep_name] = set()
                    # 添加依赖关系
                    graph[spider_name].add(dep_name)

        return graph

    def crawl(self, pattern: str) -> None:
        """并发运行爬虫"""
        logger.info(f"Starting crawl with pattern: {pattern}")
        self._running = True  # 重置运行状态

        # 构建依赖图
        logger.info("Building dependency graph...")
        graph = self._build_dependency_graph(pattern)
        if not graph:
            logger.warning(f"No matching spiders found for pattern: {pattern}")
            return

        # 创建拓扑排序器
        sorter = TopologicalSorter(graph)
        sorter.prepare()
        logger.info(f"Found {len(graph)} spiders to run with max_workers={self.max_workers}")

        # 使用线程池执行任务
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            running_tasks = {}  # future -> spider_name 映射

            while sorter.is_active() and self._running:
                # 提交新的准备好的任务
                ready_nodes = sorter.get_ready()

                # 添加日志以便调试
                if ready_nodes:
                    logger.debug(f"Got ready nodes: {ready_nodes}")
                elif not running_tasks:
                    logger.debug("No ready nodes and no running tasks")
                    break  # 如果没有准备好的节点且没有运行中的任务，退出循环

                for spider_name in ready_nodes:
                    spider_class = SpiderMeta.get(spider_name)
                    logger.info(f"Submitting spider to thread pool: {spider_name}")
                    future = executor.submit(self._run_spider, spider_class)
                    running_tasks[future] = spider_name

                # 等待任意任务完成
                if running_tasks:
                    done, _ = next(as_completed(running_tasks)), None
                    spider_name = running_tasks.pop(done)
                    try:
                        done.result()  # 检查是否有异常
                        sorter.done(spider_name)  # 标记任务完成
                        logger.info(f"Spider {spider_name} marked as done in dependency graph")
                    except Exception as e:
                        logger.error(f"Spider {spider_name} failed in thread pool with error: {str(e)}")
                        self.stop()
                        raise
                elif not ready_nodes:  # 如果没有运行中的任务且没有准备好的节点
                    break

            logger.info("All spiders completed successfully")

    def _run_spider(self, spider_class: Type[Spider]) -> None:
        """运行单个爬虫"""
        spider = spider_class(self.settings)
        spider_name = spider_class.__name__
        logger.info(f"Starting spider: {spider_name}")
        with self._lock:
            self._running_spiders.append(spider)
        try:
            spider.start()
            logger.info(f"Spider {spider_name} completed successfully")
            with self._lock:
                self._results.append({"spider_name": spider_name, "success": True, "err_msg": ""})
        except Exception as e:
            logger.error(f"Spider {spider_name} failed with error: {str(e)}")
            with self._lock:
                self._results.append({"spider_name": spider_name, "success": False, "err_msg": str(e)})
            raise
        finally:
            with self._lock:
                spider.close()
                self._running_spiders.remove(spider)
                logger.debug(f"Spider {spider_name} closed and removed from running list")

    def stop(self) -> None:
        """停止所有运行中的爬虫"""
        logger.info("Stopping all running spiders...")
        self._running = False  # 设置停止标志

        with self._lock:
            if self._running_spiders:
                for spider in self._running_spiders:
                    spider.close()
                logger.info(f"Closed {len(self._running_spiders)} running spiders")
                self._running_spiders.clear()
            else:
                logger.info("No active spiders to stop")

    def get_results(self) -> List[Dict[str, Any]]:
        """获取所有爬虫的运行结果

        Returns:
            List[Dict[str, Any]]: 包含每个爬虫运行结果的字典列表
            每个字典包含以下字段:
            - spider_name: 爬虫名称
            - success: 是否运行成功
            - err_msg: 错误信息(如果失败)
        """
        return self._results.copy()
