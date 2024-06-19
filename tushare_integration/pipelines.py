# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import logging

import pandas as pd
import yaml
from scrapy.exceptions import DropItem

from tushare_integration.db_engine import DatabaseEngineFactory
from tushare_integration.settings import TushareIntegrationSettings


class BasePipeline(object):
    def __init__(self, settings: TushareIntegrationSettings, *args, **kwargs):
        self.settings: TushareIntegrationSettings = settings
        self.schema: dict = {}

    def get_schema(self, schema: str):
        with open(f"tushare_integration/schema/{schema}.yaml", "r", encoding="utf-8") as f:
            self.schema = yaml.safe_load(f.read())

        return self.schema

    def open_spider(self, spider):
        self.schema = self.get_schema(spider.get_schema_name())

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=TushareIntegrationSettings.model_validate(
                yaml.safe_load(open('config.yaml', 'r', encoding='utf8').read())
            )
        )


class TushareIntegrationFillNAPipeline(BasePipeline):
    @staticmethod
    def get_default_by_data_type(data_type: str):
        if data_type is None:
            raise ValueError("data_type is None")

        match data_type:
            case "str":
                return ""
            case "float":
                return 0.0
            case "int":
                return 0
            case "number":
                return 0.0
            case "date":
                return "1970-01-01"
            case "datetime":
                return "1970-01-01 00:00:00"
            case 'json':
                return '{}'
            case _:
                raise ValueError(f"Unsupported data_type: {data_type}")

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if data is None or len(data) == 0:
            raise DropItem()

        for column in self.schema["columns"]:
            if column.get("default", None) is None:
                column["default"] = self.get_default_by_data_type(column["data_type"])
            # 需要特殊处理NaT,Pandas的fillna方法不支持NaT
            data[column["name"]] = data[column["name"]].replace({pd.NaT: None}).fillna(column["default"])

        return item


class TransformDTypePipeline(BasePipeline):
    def process_item(self, item, spider):
        data = item["data"]
        for column in self.schema["columns"]:
            match column["data_type"]:
                case "str":
                    data[column["name"]] = data[column["name"]].astype(str)
                case "float":
                    data[column["name"]] = data[column["name"]].astype(float)
                case "int":
                    data[column["name"]] = data[column["name"]].astype(int)
                case "number":
                    data[column["name"]] = data[column["name"]].astype(float)
                case "date":
                    data[column["name"]] = pd.to_datetime(data[column["name"]], format='mixed', errors='coerce').dt.date
                    data[column["name"]] = data[column["name"]].replace({pd.NaT: pd.to_datetime('1971-01-01').date()})
                case "datetime":
                    data[column["name"]] = pd.to_datetime(data[column["name"]])
                case 'json':
                    data[column["name"]] = data[column["name"]].apply(lambda x: '{}' if pd.isna(x) else x)
                case _:
                    raise ValueError(f"Unsupported data_type: {column['data_type']}")
        return item


class TushareIntegrationDataPipeline(BasePipeline):
    def __init__(self, settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)

        self.db_engine = DatabaseEngineFactory.create(self.settings)

        self.table_name: str = ""
        self.truncate: bool = False

    def open_spider(self, spider):
        super().open_spider(spider)
        self.table_name = spider.get_table_name()

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if data.empty:
            return item

        if (primary_key := self.schema.get("primary_key", None)) is not None:
            data = data.drop_duplicates(subset=primary_key, keep="last")
            self.db_engine.upsert(self.table_name, schema=self.schema, data=data)
        else:
            logging.debug(f"Insert data into {self.table_name}, data count: {len(data)}")
            self.db_engine.insert(self.table_name, schema=self.schema, data=data)

        return item


class RecordLogPipeline(BasePipeline):
    def __init__(self, settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)

        self.db_engine = DatabaseEngineFactory.create(self.settings)

        self.table_name: str = "tushare_integration_log"

        self.count: int = 0
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.create_log_table()

    def create_log_table(self):
        schema = {
            'primary_key': ['batch_id'],
            'columns': [
                {
                    'name': 'batch_id',
                    'data_type': 'str',
                    'comment': '批次ID',
                },
                {
                    'name': 'spider_name',
                    'data_type': 'str',
                    'comment': '爬虫名称',
                },
                {
                    'name': 'description',
                    'data_type': 'str',
                    'comment': '描述',
                },
                {
                    'name': 'count',
                    'data_type': 'int',
                    'comment': '数量',
                },
                {
                    'name': 'start_time',
                    'data_type': 'datetime',
                    'comment': '开始时间',
                },
                {
                    'name': 'end_time',
                    'data_type': 'datetime',
                    'comment': '结束时间',
                },
            ],
        }

        self.db_engine.create_table(self.table_name, schema)

    def open_spider(self, spider):
        super().open_spider(spider)
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def close_spider(self, spider):
        statistics_data = pd.DataFrame(
            [
                {
                    "batch_id": spider.settings.get("BATCH_ID", ''),
                    "spider_name": spider.name,
                    "description": self.schema.get("title", ""),
                    "count": self.count,
                    "start_time": self.start_time,
                    "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            ]
        )

        statistics_data[['start_time', 'end_time']] = statistics_data[['start_time', 'end_time']].apply(pd.to_datetime)

        self.db_engine.insert(self.table_name, self.schema, statistics_data)

    def process_item(self, item, spider):
        self.count += len(item["data"])
        return item
