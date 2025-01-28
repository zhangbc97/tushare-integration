import logging
import signal
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy import select

from tushare_integration.crawler.crawler import Crawler
from tushare_integration.crawler.pipeline import TushareIntegrationLog
from tushare_integration.db_engine import DBEngine
from tushare_integration.logger import get_logger
from tushare_integration.reporters import ReporterLoader
from tushare_integration.settings import TushareIntegrationSettings, load_config

logger = get_logger()


class TushareIntegrationManager(object):

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
        self.reporter_loader: ReporterLoader = ReporterLoader(self.settings)
        logger.info(f"Load reporters: {self.reporter_loader.get_reporters()}")

        self.crawler: Crawler | None = None

        # 注册系统信号处理器
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def run_spider(self, pattern: str) -> None:
        self.crawler = Crawler(self.settings)
        self.crawler.crawl(pattern)

    def run_job(self, job_file: str, job_name: str) -> None: ...

    def get_settings(self) -> Dict[str, Any]:
        """获爬虫设置"""
        settings = self.settings.get_settings()
        settings['LOG_LEVEL'] = 'INFO'
        settings['BATCH_ID'] = self.batch_id
        return settings

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

            # TODO 添TODO加警告信息

            return content

    def stop(self, signum: int, frame: Any) -> None:
        """停止爬虫"""
        logger.warning("Received stop signal, stopping...")
        if self.crawler:
            self.crawler.stop()
        self.send_report()
