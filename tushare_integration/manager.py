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

        self.process = scrapy.crawler.CrawlerProcess(self.get_settings())
        self.db_engine: DBEngine = DBEngine(self.settings)
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
            爬虫信息列表，每个元素包含api_title、name和api_path
        """
        # 获取spiders列表
        spider_names = self.process.spider_loader.list()
        # 过滤
        if pattern:
            spider_names = [s for s in spider_names if re.fullmatch(pattern, s)]

        spider_info_list = []
        for spider_name in spider_names:
            # 获取spider类
            spider_cls = self.process.spider_loader.load(spider_name)
            # 获取model类
            model = getattr(spider_cls, '__model__', None)
            if model:
                spider_info_list.append(
                    {
                        'api_title': getattr(model, '__api_title__', ''),
                        'name': spider_name,
                        'api_path': ' > '.join(getattr(model, '__api_path__', [])),
                    }
                )

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
            所有需要运行的爬虫名称列表（按依赖顺序排序）
        """
        # 确保spiders列表中的每个元素都是字符串（spider名称）
        dependencies = [spiders]

        # 采��服不是并行的，开启依赖析的情况下可能会导致数据出现重复等问题
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

        # 运行第一个爬虫
        deferred = self.process.crawl(spiders[0])

        # 如果还有其他爬虫，添加到回调中
        if len(spiders) > 1:
            deferred.addCallback(lambda _: self.run_spiders_in_sequence(spiders[1:]))

        return deferred

    def run_spider(self, spider: str) -> None:
        """运行指定爬虫

        Args:
            spider: 爬虫名称（支持通配符）
        """
        # 获取匹配的爬虫
        spiders = self.list_spiders(spider)
        if not spiders:
            console.print(f"[red]未找到匹配的爬虫: {spider}[/red]")
            return

        # 获取所有需要运行的爬虫
        spider_names = [s['name'] for s in spiders]
        all_spiders = self.get_all_spiders(spider_names)

        # 运行爬虫
        console.print(f"[yellow]运行爬虫: {', '.join(all_spiders)}[/yellow]")
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
        spiders = [spider['name'] for spider in job.get('spiders', [])]
        all_spiders = self.get_all_spiders(spiders)

        # 运行爬虫
        console.print(f"[yellow]运行任务: {job_name}[/yellow]")
        console.print(f"[yellow]运行爬虫: {', '.join(all_spiders)}[/yellow]")
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
            spiders = [spider['name'] for spider in job.get('spiders', [])]
            all_spiders.extend(self.get_all_spiders(spiders))

        # 去重并保持顺序
        all_spiders = list(dict.fromkeys(all_spiders))

        # 运行��虫
        console.print(f"[yellow]运行爬虫: {', '.join(all_spiders)}[/yellow]")
        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        # 发送报告
        self.send_report()

        # 如果有异常就抛出
        self.raise_for_signal()

    def get_settings(self) -> Dict[str, Any]:
        """获取爬虫设置"""
        settings = {
            'ROBOTSTXT_OBEY': False,
            'CONCURRENT_REQUESTS': self.settings.tushare_point // 100,
            'CONCURRENT_REQUESTS_PER_DOMAIN': self.settings.tushare_point // 100,
            'CONCURRENT_REQUESTS_PER_IP': self.settings.tushare_point // 100,
            'DOWNLOAD_DELAY': 0.1,
            'COOKIES_ENABLED': False,
            'TELNETCONSOLE_ENABLED': False,
            'LOG_LEVEL': 'INFO',
            'TUSHARE_TOKEN': self.settings.tushare_token,
            'TUSHARE_URL': self.settings.tushare_url,
            'BATCH_ID': self.batch_id,
            'DB_ENGINE': self.db_engine,
        }
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
        """记录���虫信号"""
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

            content = f"批次ID: {self.batch_id}\n\n"

            # 添加爬虫运行状态
            for log in logs:
                content += f"爬虫: {log.spider_name} 数据数量: {log.count}\n"

            # 添加警告信息
            if self.signals:
                content += "警告信息：\n"
                for scrapy_signal in self.signals:
                    if scrapy_signal['signal'] == scrapy.signals.item_error:
                        content += f"爬虫: {scrapy_signal['spider'].name}\n"
                        content += "警告: 数据项错误\n"
                        if scrapy_signal.get('reason'):
                            content += f"原因: {scrapy_signal['reason']}\n"
                        content += "\n"
                    elif scrapy_signal['signal'] == scrapy.signals.spider_error:
                        content += f"爬虫: {scrapy_signal['spider'].name}\n"
                        content += "警告: 爬虫错误\n"
                        if scrapy_signal.get('reason'):
                            content += f"原因: {scrapy_signal['reason']}\n"
                        content += "\n"

            return content

    def raise_for_signal(self) -> None:
        """如果有错误信号就抛出异常"""
        if self.signals:
            raise Exception(f"爬虫运行出错: {self.signals}")

    def stop(self, signum: int, frame: Any) -> None:
        """停止爬虫"""
        console.print("[yellow]收到停止信号，正在停止...[/yellow]")
        self.process.stop()
        self.send_report()
