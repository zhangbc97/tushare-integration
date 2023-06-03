# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import logging

import pandas as pd
import yaml
# useful for handling different item types with a single interface
from sqlalchemy import create_engine, text

from tushare_integration.schema.sql_template import SQLTemplate
from tushare_integration.settings import TushareIntegrationSettings


class BasePipeline(object):
    schema = None

    def __init__(self, settings: TushareIntegrationSettings, *args, **kwargs):
        self.settings: TushareIntegrationSettings = settings

    def get_schema(self, schema: str):
        with open(
                f"tushare_integration/schema/{schema}.yaml", "r", encoding="utf-8"
        ) as f:
            self.schema = yaml.safe_load(f.read())

        return self.schema

    def open_spider(self, spider):
        self.schema = self.get_schema(spider.get_schema_name())


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
            case _:
                raise ValueError(f"Unsupported data_type: {data_type}")

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if not data or len(data) == 0:
            return

        for column in self.schema["outputs"]:
            if column.get("default", None) is None:
                column["default"] = self.get_default_by_data_type(column["data_type"])
            # 需要特殊处理NaT,Pandas的fillna方法不支持NaT
            data[column["name"]] = data[column["name"]].replace({pd.NaT: None}).fillna(column["default"])
        return item


class TransformDTypePipeline(BasePipeline):

    def process_item(self, item, spider):
        data = item["data"]
        for column in self.schema["outputs"]:
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
                    data[column["name"]] = data[column["name"]].replace({pd.NaT: pd.to_datetime('1970-01-01').date()})
                case "datetime":
                    data[column["name"]] = pd.to_datetime(data[column["name"]])
                case _:
                    raise ValueError(f"Unsupported data_type: {column['data_type']}")
        return item


class TushareIntegrationDataPipeline(BasePipeline):

    def __init__(self,settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)
        self.template = SQLTemplate(self.settings)
        self.db_uri: str = self.settings.db_uri
        self.db_name: str = self.settings.db_name
        self.table_name: str = ""
        self.truncate: bool = False

        self.engine = create_engine(self.db_uri)
        self.conn = self.engine.connect()

    def open_spider(self, spider):
        super().open_spider(spider)
        self.table_name = spider.get_table_name()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if data.empty:
            return item

        if (primary_key := self.schema.get("primary_key", None)) is not None:
            data = data.drop_duplicates(subset=primary_key.split(","), keep="last")
            self.conn.execute(
                text(
                    self.template.upsert_data(self.db_name, self.table_name, data.columns.tolist(), primary_key)
                ),
                data.to_dict("records")
            )

        else:
            logging.debug(f"Insert data into {self.table_name}, data count: {len(data)}")
            self.conn.execute(
                text(
                    self.template.insert_data(self.db_name, self.table_name, data.columns.tolist())
                ),
                data.to_dict("records")
            )

        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)


class RecordLogPipeline(BasePipeline):
    def __init__(self, settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)
        self.template = SQLTemplate(self.settings)
        self.db_uri: str = self.settings.db_uri
        self.db_name: str = self.settings.db_name
        self.table_name: str = "tushare_integration_log"

        self.count: int = 0
        self.engine = create_engine(self.db_uri)
        self.conn = self.engine.connect()
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.create_log_table()

    def create_log_table(self):
        schema = {
            'outputs': [
                {
                    'name': 'batch_id',
                    'data_type': 'str',
                    'description': '批次ID',
                },
                {
                    'name': 'spider_name',
                    'data_type': 'str',
                    'desc': '爬虫名称',
                },
                {
                    'name': 'description',
                    'data_type': 'str',
                    'desc': '描述',
                },
                {
                    'name': 'count',
                    'data_type': 'int',
                    'desc': '数量',
                },
                {
                    'name': 'start_time',
                    'data_type': 'datetime',
                    'desc': '开始时间',
                },
                {
                    'name': 'end_time',
                    'data_type': 'datetime',
                    'desc': '结束时间',
                },

            ]
        }

        self.conn.execute(text(self.template.create_table(self.db_name, self.table_name, schema=schema)))

    def open_spider(self, spider):
        super().open_spider(spider)
        self.start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def close_spider(self, spider):
        # 将总数写入数据库
        self.conn.execute(text(self.template.insert_data(
            self.db_name,
            self.table_name,
            ["batch_id", "spider_name", "description", "count", "start_time", "end_time"])
        ),
            parameters={
                "batch_id": spider.settings.get("BATCH_ID", ''),
                "spider_name": spider.name,
                "description": self.schema.get("title", ""),
                "count": self.count,
                "start_time": self.start_time,
                "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def process_item(self, item, spider):
        self.count += len(item["data"])
        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(settings=crawler.settings)
