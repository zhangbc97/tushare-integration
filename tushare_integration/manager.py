import itertools
import logging
import re
import uuid

import scrapy.crawler
import scrapy.signals
import yaml
from scrapy.signalmanager import dispatcher
from sqlalchemy import create_engine, text

from tushare_integration.reporters import ReporterLoader
from tushare_integration.settings import TushareIntegrationSettings


class CrawlManager(object):

    def __init__(self):
        self.batch_id = uuid.uuid1().hex
        self.settings = TushareIntegrationSettings.parse_file(
            'config.yaml'
        ).get_settings()

        self.process = scrapy.crawler.CrawlerProcess(self.get_settings())

        self.signals = []
        dispatcher.connect(self.append_signal, signal=scrapy.signals.item_error)
        dispatcher.connect(self.append_signal, signal=scrapy.signals.spider_error)

    def list_spiders(self, spider: str = None) -> list[str]:
        """
        列出所有spider
        :param spider: 通配符
        :return: spider列表
        """
        # 获取spiders列表
        spiders = self.process.spider_loader.list()
        # 过滤
        if spider:
            spiders = [s for s in spiders if re.match(spider, s)]
        return spiders

    def append_signal(self, signal, sender, item, response, spider):
        if not any([s['signal'] == signal and s['spider'] == spider for s in self.signals]):
            self.signals.append(
                {'signal': signal, 'sender': sender, 'item': item, 'response': response, 'spider': spider}
            )

    def get_settings(self):
        self.settings.update({
            'LOG_LEVEL': 'INFO',
            'BATCH_ID': self.batch_id,
        })
        return self.settings

    def get_spiders_by_job(self, job_name: str) -> list[str]:
        with open("jobs.yaml", 'r', encoding='utf8') as f:
            jobs = yaml.safe_load(f.read())
        for job in jobs['cronjob']:
            if job['name'] == job_name:
                return list(
                    set(list(itertools.chain(*[self.list_spiders(spider['name']) for spider in job['spiders']]))))
        raise ValueError(f"Job {job_name} not found")

    def run_job(self, job_name: str):
        for spider in self.get_spiders_by_job(job_name):
            logging.info(f"Add spider {spider}...")
            self.process.crawl(spider)

        self.process.start()

    def run_spider(self, spider: str):
        for spider in self.list_spiders(spider):
            logging.info(f"Add spider {spider}...")
            self.process.crawl(spider)

        self.process.start()
        self.report()

    def get_report_content(self):
        content = f"批次ID：{self.batch_id}\n"
        engine = create_engine(self.settings.get('DB_URI'))
        conn = engine.connect()
        for row in conn.execute(
                text(
                    f'select description,count from {self.settings.get("DB_NAME")}.tushare_integration_log '
                    f'where batch_id = :batch_id'
                ),
                parameters={'batch_id': self.batch_id}):
            content += f"爬虫名称:{row[0]}  数据数量:{row[1]}\n"

        if self.signals:
            content += "警告信息：\n"
            for signal in self.signals:
                if signal['signal'] == scrapy.signals.item_error:
                    content += f"爬虫名称:{signal['spider'].name} 警告信息:item error\n"
                elif signal['signal'] == scrapy.signals.spider_error:
                    content += f"爬虫名称:{signal['spider'].name} 警告信息:spider error\n"
        return content

    def report(self):
        reporter_loader = ReporterLoader(self.settings)

        for reporter in reporter_loader.get_reporters():
            reporter.send_report(
                subject='数据更新通知',
                content=self.get_report_content()
            )
