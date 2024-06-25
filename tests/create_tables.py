import logging
import os
import sys

import yaml

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tushare_integration.db_engine import DatabaseEngineFactory
from tushare_integration.manager import CrawlManager
from tushare_integration.settings import TushareIntegrationSettings


def main():
    manager = CrawlManager()
    settings = TushareIntegrationSettings.model_validate(yaml.safe_load(open('config.yaml', 'r', encoding='utf-8')))
    for spider in manager.list_spiders('.*'):
        table_name = spider.split('/')[-1]

        schema = yaml.safe_load(open(f"tushare_integration/schema/{spider}.yaml", "r", encoding="utf-8").read())
        db_engine = DatabaseEngineFactory.create(settings)
        try:
            logging.info(f"Creating table {table_name}")
            db_engine.create_table(table_name, schema)
        except Exception as e:
            print(spider, e)


if __name__ == '__main__':
    main()
