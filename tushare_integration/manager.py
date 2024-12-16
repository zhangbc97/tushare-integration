import re
import signal
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import scrapy.crawler
import scrapy.signals
import yaml
from rich.console import Console
from scrapy.signalmanager import dispatcher
from sqlalchemy import select
from twisted.internet.defer import Deferred

from tushare_integration.db_engine import DBEngine
from tushare_integration.log_model import TushareIntegrationLog
from tushare_integration.reporters import ReporterLoader
from tushare_integration.settings import TushareIntegrationSettings, load_config
from tushare_integration.dictionary import API_PATH_DICTIONARY

console = Console()


class CrawlManager(object):
    """爬虫管理器"""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """初始化爬虫管理器

        Args:
            config_file: 配置文件路径，默认为当前目录下的config.yaml
        """
        if config_file is None:
            config_file = Path('config.yaml')

        # 检查配置文件
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        # 加载配置
        self.config_file = config_file
        self.batch_id = uuid.uuid1().hex
        self.settings: TushareIntegrationSettings = load_config(config_file)
        self.db_engine: DBEngine = DBEngine(self.settings)
        self.process = scrapy.crawler.CrawlerProcess(self.get_settings())
        self.reporter_loader: ReporterLoader = ReporterLoader(self.settings)

        # 注册信号处理器
        self.signals: List[Dict[str, Any]] = []
        dispatcher.connect(self.append_signal, signal=scrapy.signals.spider_closed)
        dispatcher.connect(self.append_signal, signal=scrapy.signals.spider_error)
        dispatcher.connect(self.append_signal, signal=scrapy.signals.item_error)

        # 注册系统信号处理器
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def list_spiders(self, pattern: Optional[str] = None) -> List[Dict[str, str]]:
        """列出所有爬虫

        Args:
            pattern: 爬虫名称匹配模式

        Returns:
            爬虫信息列表，每个元素包含api_title、name、api_path和api_path_en
        """
        # 获取spiders列表
        spider_names = self.process.spider_loader.list()
        # 过滤
        if pattern:
            spider_names = [s for s in spider_names if re.fullmatch(pattern, s)]

        # 创建中文到英文的映射字典
        cn_to_en_dict = {k: v for k, v in API_PATH_DICTIONARY.items()}

        spider_info_list = []
        for spider_name in spider_names:
            # 获取spider类
            spider_cls = self.process.spider_loader.load(spider_name)
            # 获取model类
            model = getattr(spider_cls, '__model__', None)
            if model:
                api_path = getattr(model, '__api_path__', [])
                # 转换为英文路径，跳过第一个元素
                api_path_en = []
                for i, path in enumerate(api_path[1:], 1):  # 从第二个元素开始，保持索引正确
                    if i == len(api_path) - 1:
                        # 最后一级使用__api_name__
                        api_path_en.append(getattr(model, '__api_name__', path))
                    else:
                        en_path = cn_to_en_dict.get(path, path)
                        api_path_en.append(en_path)

                spider_info_list.append({
                    'api_title': getattr(model, '__api_title__', ''),
                    'name': spider_name,
                    'api_path': ' > '.join(api_path),
                    'api_path_en': '/'.join(api_path_en),
                })

        return spider_info_list

    def get_dependencies(self, spiders: List[str]) -> List[str]:
        """获取爬虫依赖

        Args:
            spiders: 爬虫名称列表

        Returns:
            依赖的爬虫名称列表
        """
        dependencies = []
        for spider_name in spiders:
            # 获取spider类
            spider_cls = self.process.spider_loader.load(spider_name)
            # 获取model类
            model = getattr(spider_cls, '__model__', None)
            if model and hasattr(model, '__dependencies__'):
                dependencies.extend(model.__dependencies__)

        return list(set(dependencies))

    def get_all_spiders(self, spiders: List[str]) -> List[str]:
        """获取所有需运行的爬虫（包括依赖）

        Args:
            spiders: 爬虫名称列表

        Returns:
            所有需要运行的爬虫名称列表（按赖顺序排序）
        """
        # 确保spiders列表中的每个元素都是字符串（spider名称）
        dependencies = [spiders]

        # 采服不是并行的，开启依赖析的情况下可能会导致数据出现重复等问题
        if not self.settings.parallel_mode:
            while self.get_dependencies(dependencies[-1]):
                dependencies.append(self.get_dependencies(dependencies[-1]))

        all_spiders = []
        # 从列表最后一个开始，因为最后一个是最底层的依赖
        for dependency in reversed(dependencies):
            for spider in dependency:
                if spider not in all_spiders:
                    all_spiders.append(spider)

        return all_spiders

    def run_spiders_in_sequence(self, spiders: List[str]) -> Optional[Deferred]:
        """按顺序运行爬虫

        Args:
            spiders: 爬虫名称列表

        Returns:
            Deferred对象，如果有爬虫需要运行
        """
        if not spiders:
            return None

        # 添加开始爬取的日志输出
        console.print(f"[blue]Start crawling: {spiders[0]}[/blue]")

        # 运行第一个爬虫
        deferred = self.process.crawl(spiders[0])

        # 如果还有其他爬虫，添加到回调中
        if len(spiders) > 1:
            deferred.addCallback(lambda _: self.run_spiders_in_sequence(spiders[1:]))

        return deferred

    def _get_spiders_by_pattern(self, pattern: str) -> List[Dict[str, str]]:
        """内部方法：根据模式获取爬虫列表
        
        Args:
            pattern: 爬虫名称或API路径模式
        
        Returns:
            匹配的爬虫列表
        """
        if '/' in pattern:
            return self._list_spiders_by_path(pattern)
        else:
            return self.list_spiders(pattern)

    def run_spider(self, spider: str) -> None:
        """运行指定爬虫

        Args:
            spider: 爬虫名称（支持通配符）或API路径模式（如 'stock/basic'）
        """
        spiders = self._get_spiders_by_pattern(spider)
        if not spiders:
            console.print(f"[red]No matching spider found: {spider}[/red]")
            return

        # 获取所有需要运行的爬虫
        spider_names = [s['name'] for s in spiders]
        all_spiders = self.get_all_spiders(spider_names)

        # 运行爬虫
        console.print(f"[yellow]Running spiders: {', '.join(all_spiders)}[/yellow]")
        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        # 发送报告
        self.send_report()

        # 如果有异常就抛出
        self.raise_for_signal()

    def run_job(self, job_name: str) -> None:
        """运行预定义任务

        Args:
            job_name: 任务名称
        """
        # 获取任务配置文件路径
        jobs_file = self.config_file.parent / 'jobs.yaml'
        if not jobs_file.exists():
            raise FileNotFoundError(f"任务配置文件不存在: {jobs_file}")

        # 加载任务配置
        jobs_config = yaml.safe_load(jobs_file.read_text())

        # 查找任务
        job = None
        for j in jobs_config.get('jobs', []):
            if j.get('name') == job_name:
                job = j
                break

        if job is None:
            raise ValueError(f"任务不存在: {job_name}")

        # 获取所有需要运行的爬虫
        all_spiders = []
        for spider_pattern in job.get('spiders', []):
            spiders = self._get_spiders_by_pattern(spider_pattern['name'])
            if spiders:
                all_spiders.extend([s['name'] for s in spiders])
            else:
                console.print(f"[yellow]Warning: No matching spider found for: {spider_pattern['name']}[/yellow]")

        if not all_spiders:
            raise ValueError(f"任务中未找到任何匹配的爬虫")

        # 获取所有依赖
        all_spiders = self.get_all_spiders(all_spiders)

        # 运行爬虫
        console.print(f"[yellow]Running job: {job_name}[/yellow]")
        console.print(f"[yellow]Running spiders: {', '.join(all_spiders)}[/yellow]")
        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        # 发送报告
        self.send_report()

        # 如果有异常就抛出
        self.raise_for_signal()

    def run_job_file(self, job_file: Path) -> None:
        """运行任务配置文件

        Args:
            job_file: 任务配置文件路径
        """
        if not job_file.exists():
            raise FileNotFoundError(f"任务配置文件不存在: {job_file}")

        # 加载任务配置
        jobs_config = yaml.safe_load(job_file.read_text())

        # 获取所有需要运行的爬虫
        all_spiders = []
        for job in jobs_config.get('jobs', []):
            for spider_pattern in job.get('spiders', []):
                spiders = self._get_spiders_by_pattern(spider_pattern['name'])
                if spiders:
                    all_spiders.extend([s['name'] for s in spiders])
                else:
                    console.print(f"[yellow]Warning: No matching spider found for: {spider_pattern['name']}[/yellow]")

        if not all_spiders:
            raise ValueError(f"任务文件中未找到任何匹配的爬虫")

        # 去重并获取所有依赖
        all_spiders = self.get_all_spiders(list(dict.fromkeys(all_spiders)))

        # 运行爬虫
        console.print(f"[yellow]Running spiders: {', '.join(all_spiders)}[/yellow]")
        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        # 发送报告
        self.send_report()

        # 如果有异常就抛出
        self.raise_for_signal()

    def get_settings(self) -> Dict[str, Any]:
        """获爬虫设置"""
        settings = self.settings.get_settings()
        settings['LOG_LEVEL'] = 'INFO'
        settings['BATCH_ID'] = self.batch_id
        return settings

    def append_signal(
        self,
        signal: Optional[Any] = None,
        sender: Optional[Any] = None,
        item: Optional[Any] = None,
        response: Optional[Any] = None,
        spider: Optional[Any] = None,
        reason: Optional[str] = None,
    ) -> None:
        """记录信号"""
        # 记录信号
        if signal in [scrapy.signals.spider_error, scrapy.signals.item_error]:
            if not any(s['signal'] == signal and s['spider'] == spider for s in self.signals):
                self.signals.append(
                    {
                        'signal': signal,
                        'spider': spider,
                        'reason': reason,
                    }
                )

        # 记录日志
        if spider is not None:
            with self.db_engine.session() as session:
                log = TushareIntegrationLog(
                    batch_id=self.batch_id,
                    spider_name=spider.name,
                    status='error' if reason else 'success',
                    reason=str(reason) if reason else None,
                )
                session.add(log)
                session.commit()

    def send_report(self) -> None:
        """发送报告"""
        for reporter in self.reporter_loader.get_reporters():
            reporter.send_report(subject='数据更新通知', content=self.get_report_content())

    def get_report_content(self) -> str:
        """获取报告内容"""
        with self.db_engine.session() as session:
            logs = (
                session.execute(select(TushareIntegrationLog).where(TushareIntegrationLog.batch_id == self.batch_id))
                .scalars()
                .all()
            )

            content = f"Batch ID: {self.batch_id}\n\n"

            # 添加爬虫运行状态
            for log in logs:
                content += f"Spider: {log.spider_name} Count: {log.count}\n"

            # 添加警告信息
            if self.signals:
                content += "Warnings:\n"
                for scrapy_signal in self.signals:
                    if scrapy_signal['signal'] == scrapy.signals.item_error:
                        content += f"Spider: {scrapy_signal['spider'].name}\n"
                        content += "Warning: Item Error\n"
                        if scrapy_signal.get('reason'):
                            content += f"Reason: {scrapy_signal['reason']}\n"
                        content += "\n"
                    elif scrapy_signal['signal'] == scrapy.signals.spider_error:
                        content += f"Spider: {scrapy_signal['spider'].name}\n"
                        content += "Warning: Spider Error\n"
                        if scrapy_signal.get('reason'):
                            content += f"Reason: {scrapy_signal['reason']}\n"
                        content += "\n"

            return content

    def raise_for_signal(self) -> None:
        """如果有错误信号就抛出异常"""
        if self.signals:
            raise Exception(f"爬虫运行出错: {self.signals}")

    def stop(self, signum: int, frame: Any) -> None:
        """停止爬虫"""
        console.print("[yellow]Received stop signal, stopping...[/yellow]")
        self.process.stop()
        self.send_report()

    def _list_spiders_by_path(self, path_pattern: str) -> List[Dict[str, str]]:
        """内部方法：通过API路径模式匹配爬虫
        
        Args:
            path_pattern: API路径匹配模式，如 'stock/basic'
        
        Returns:
            匹配的爬虫列表
        """
        path_parts = path_pattern.strip('/').split('/')
        cn_path_parts = []
        
        # 创建反向映射字典
        reverse_dict = {v: k for k, v in API_PATH_DICTIONARY.items()}
        
        for part in path_parts:
            if part in reverse_dict:
                cn_path_parts.append(reverse_dict[part])
            else:
                cn_path_parts.append(part)
        
        spider_names = self.process.spider_loader.list()
        spider_info_list = []
        
        for spider_name in spider_names:
            spider_cls = self.process.spider_loader.load(spider_name)
            model = getattr(spider_cls, '__model__', None)
            
            if model and hasattr(model, '__api_path__'):
                api_path = model.__api_path__
                
                # 跳过第一个元素进行匹配
                match = True
                for i, pattern in enumerate(cn_path_parts):
                    # 直接从第二个元素开始匹配
                    api_path_index = i + 1
                    if api_path_index >= len(api_path):
                        match = False
                        break
                    if not re.fullmatch(pattern, api_path[api_path_index]):
                        match = False
                        break
                
                if match:
                    # 转换为英文路径，跳过第一个元素
                    api_path_en = []
                    for i, path in enumerate(api_path[1:], 1):  # 从第二个元素开始，保持索引正确
                        if i == len(api_path) - 1:
                            # 最后一级使用__api_name__
                            api_path_en.append(getattr(model, '__api_name__', path))
                        else:
                            en_path = reverse_dict.get(path, path)
                            api_path_en.append(en_path)

                    spider_info_list.append({
                        'api_title': getattr(model, '__api_title__', ''),
                        'name': spider_name,
                        'api_path': ' > '.join(api_path),
                        'api_path_en': '/'.join(api_path_en),
                    })
        
        return spider_info_list
