import itertools
import logging
import re
import signal
import uuid

import scrapy.crawler
import scrapy.signals
import yaml
from scrapy.signalmanager import dispatcher

from tushare_integration.db_engine import DatabaseEngineFactory
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

    def list_spiders(self, spider: str | None = None) -> list[str]:
        """
        列出所有spider
        :param spider: 通配符
        :return: spider列表
        """
        # 获取spiders列表
        spiders = self.process.spider_loader.list()
        # 过滤
        if spider:
            spiders = [s for s in spiders if re.fullmatch(spider, s)]
        return spiders

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
                return list(
                    set(list(itertools.chain(*[self.list_spiders(spider['name']) for spider in job['spiders']])))
                )
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
        # 如果有异常就抛出
        self.raise_for_signal()

    def get_all_spiders(self, spiders):
        dependencies = [spiders]
        # 采集服务不是并发安全的，开启依赖解析的情况下可能会导致数据出现重复等问题
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

        for index, row in db_engine.query_df(
            f"select description,count from {self.settings.database.db_name}.tushare_integration_log "
            f"where batch_id = '{self.batch_id}'"
        ).iterrows():
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
