import itertools
import logging
import re
import signal
import uuid

import scrapy.crawler
import scrapy.signals
import yaml
from scrapy.signalmanager import dispatcher
from sqlalchemy import select

from tushare_integration.db_engine import DatabaseEngineFactory
from tushare_integration.log_model import TushareIntegrationLog
from tushare_integration.reporters import ReporterLoader
from tushare_integration.settings import TushareIntegrationSettings


class CrawlManager(object):
    def __init__(self):
        self.batch_id = uuid.uuid1().hex
        self.settings = TushareIntegrationSettings.model_validate(
            yaml.safe_load(open('config.yaml', 'r', encoding='utf8').read())
        )

        self.process = scrapy.crawler.CrawlerProcess(self.get_settings())

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        self.signals = []
        dispatcher.connect(self.append_signal, signal=scrapy.signals.item_error)
        dispatcher.connect(self.append_signal, signal=scrapy.signals.spider_error)

    def list_spiders(self, spider: str | None = None) -> list[dict]:
        """
        列出所有spider的详细信息
        :param spider: 通配符
        :return: spider信息列表，每个元素包含api_title、name和api_path
        """
        # 获取spiders列表
        spider_names = self.process.spider_loader.list()
        # 过滤
        if spider:
            spider_names = [s for s in spider_names if re.fullmatch(spider, s)]

        spider_info_list = []
        for spider_name in spider_names:
            # 获取spider类
            spider_cls = self.process.spider_loader.load(spider_name)
            # 获取model类
            model = getattr(spider_cls, '__model__', None)

            info = {
                'api_title': getattr(model, '__api_title__', ''),
                'name': spider_name,
                'api_path': ' > '.join(getattr(model, '__api_path__', [])),
            }
            spider_info_list.append(info)

        return spider_info_list

    def append_signal(self, signal, sender=None, item=None, response=None, spider=None):
        if not any([s['signal'] == signal and s['spider'] == spider for s in self.signals]):
            self.signals.append(
                {'signal': signal, 'sender': sender, 'item': item, 'response': response, 'spider': spider}
            )

    def get_settings(self):
        settings = self.settings.get_settings()
        settings['LOG_LEVEL'] = 'INFO'
        settings['BATCH_ID'] = self.batch_id
        return settings

    @staticmethod
    def get_dependencies(spiders: list[str]) -> list[str]:
        dependencies = []
        for spider in spiders:
            with open(f"tushare_integration/schema/{spider}.yaml", 'r', encoding='utf8') as f:
                schema = yaml.safe_load(f.read())
            dependencies.extend(schema.get('dependencies', []))
        return list(set(dependencies))

    def get_spiders_by_job(self, job_name: str) -> list[str]:
        with open("jobs.yaml", 'r', encoding='utf8') as f:
            jobs = yaml.safe_load(f.read())
        for job in jobs['cronjob']:
            if job['name'] == job_name:
                # 由于list_spiders现在返回dict列表，需要提取name
                spiders_info = list(itertools.chain(*[self.list_spiders(spider['name']) for spider in job['spiders']]))
                return list(set([spider['name'] for spider in spiders_info]))
        raise ValueError(f"Job {job_name} not found")

    def run_spiders_in_sequence(self, spiders: list[str]):
        logging.error(spiders)

        if len(spiders) == 0:
            return

        deferred = self.process.crawl(spiders[0])
        if len(spiders) > 1:
            deferred.addCallback(lambda _: self.run_spiders_in_sequence(spiders[1:]))

    def run_job(self, job_name: str):
        spiders = self.get_spiders_by_job(job_name)
        all_spiders = self.get_all_spiders(spiders)

        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        self.report()
        # 如果有异常就抛出
        self.raise_for_signal()

    def run_spider(self, spider: str):
        spiders = self.list_spiders(spider)
        all_spiders = self.get_all_spiders(spiders)

        self.run_spiders_in_sequence(all_spiders)
        self.process.start()

        self.report()
        # 如果有异常直接抛出
        self.raise_for_signal()

    def get_all_spiders(self, spiders):
        dependencies = [spiders]
        # 采集服不是并发安全的，开启依赖析的情况下可能会导致数据出现重复等问题
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

    def raise_for_signal(self):
        if self.signals:
            raise Exception(f"Signals: {self.signals}")

    def get_report_content(self):
        content = f"批次ID：{self.batch_id}\n"

        db_engine = DatabaseEngineFactory.create(self.settings)

        # 使用 SQLAlchemy select 获取日志记录
        query = select(TushareIntegrationLog.description, TushareIntegrationLog.count).where(
            TushareIntegrationLog.batch_id == self.batch_id
        )

        for index, row in db_engine.query_df(query).iterrows():
            content += f"爬虫名称:{row['description']}  数据数量:{row['count']}\n"

        if self.signals:
            content += "警告信息：\n"
            for scrapy_signal in self.signals:
                if scrapy_signal['signal'] == scrapy.signals.item_error:
                    content += f"爬虫名称:{scrapy_signal['spider'].name} 警告信息:item error\n"
                elif scrapy_signal['signal'] == scrapy.signals.spider_error:
                    content += f"爬虫名称:{scrapy_signal['spider'].name} 警告信息:spider error\n"
        return content

    def report(self):
        reporter_loader = ReporterLoader(self.get_settings())

        for reporter in reporter_loader.get_reporters():
            reporter.send_report(subject='数据更新通知', content=self.get_report_content())

    def stop(self, signum, frame):
        logging.info("caught stop signal, stopping...")
        self.process.stop()
