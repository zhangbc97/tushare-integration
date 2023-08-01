import os

import yaml

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tushare_integration.settings import TushareIntegrationSettings
from tushare_integration.db_engine import DatabaseEngineFactory

from tushare_integration.manager import CrawlManager


def main():
    manager = CrawlManager()
    settings = TushareIntegrationSettings.parse_file('config.yaml')
    for spider in manager.list_spiders('.*'):
        table_name = spider.split('/')[-1]

        schema = yaml.safe_load(open(f"tushare_integration/schema/{spider}.yaml", "r", encoding="utf-8").read())
        db_engine = DatabaseEngineFactory.create(settings)
        try:
            db_engine.create_table(table_name, schema)
        except Exception as e:
            print(spider, e)


if __name__ == '__main__':
    main()
