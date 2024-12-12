# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import logging

import pandas as pd
import yaml
from scrapy.exceptions import DropItem
from sqlalchemy import Column

from tushare_integration.db_engine import DatabaseEngineFactory
from tushare_integration.log_model import TushareIntegrationLog
from tushare_integration.settings import TushareIntegrationSettings


class BasePipeline(object):
    def __init__(self, settings: TushareIntegrationSettings, *args, **kwargs):
        self.settings: TushareIntegrationSettings = settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            settings=TushareIntegrationSettings.model_validate(
                yaml.safe_load(open('config.yaml', 'r', encoding='utf8').read())
            )
        )


class TushareIntegrationFillNAPipeline(BasePipeline):
    @staticmethod
    def get_default_by_column(column: Column):
        if column is None:
            raise ValueError("column_type is None")

        type_name = column.type.python_type.__name__
        if type_name == 'str':
            return ""
        elif type_name == 'float':
            return 0.0
        elif type_name == 'int':
            return 0
        elif type_name == 'date':
            return "1970-01-01"
        elif type_name == 'datetime':
            return "1970-01-01 00:00:00"
        elif type_name == 'dict':
            return '{}'
        else:
            raise ValueError(f"Unsupported python_type: {type_name} for column_type: {column}")

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if data is None or len(data) == 0:
            raise DropItem()

        model = spider.__model__
        for column in model.__table__.columns:
            default = column.default.arg if column.default else self.get_default_by_column(column)
            # 需要特殊处理NaT,Pandas的fillna方法不支持NaT
            data[column.name] = data[column.name].replace({pd.NaT: None}).fillna(default)

        return item


class TransformDTypePipeline(BasePipeline):
    def process_item(self, item, spider):
        data = item["data"]
        model = spider.__model__
        for column in model.__table__.columns:
            python_type = column.type.python_type
            type_name = python_type.__name__
            if type_name == 'str':
                data[column.name] = data[column.name].astype(str)
            elif type_name == 'float':
                data[column.name] = data[column.name].astype(float)
            elif type_name == 'int':
                data[column.name] = data[column.name].astype(int)
            elif type_name == 'date':
                data[column.name] = pd.to_datetime(data[column.name], format='mixed', errors='coerce').dt.date
                data[column.name] = data[column.name].replace({pd.NaT: pd.to_datetime('1971-01-01').date()})
            elif type_name == 'datetime':
                data[column.name] = pd.to_datetime(data[column.name])
            elif type_name == 'dict':
                data[column.name] = data[column.name].apply(lambda x: '{}' if pd.isna(x) else x)
            else:
                raise ValueError(f"Unsupported python_type: {python_type} for column_type: {column.type}")
        return item


class TushareIntegrationDataPipeline(BasePipeline):
    def __init__(self, settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)
        self.db_engine = DatabaseEngineFactory.create(self.settings)
        self.table_name: str = ""
        self.truncate: bool = False

    def open_spider(self, spider):
        self.table_name = spider.__model__.__tablename__

    def process_item(self, item, spider):
        data: pd.DataFrame = item["data"]

        if data.empty:
            return item

        model = spider.__model__
        if model.__primary_key__:
            data = data.drop_duplicates(subset=model.__primary_key__, keep="last")
            self.db_engine.upsert(model, data=data)
        else:
            logging.debug(f"Insert data into {self.table_name}, data count: {len(data)}")
            self.db_engine.insert(model, data=data)

        return item


class RecordLogPipeline(BasePipeline):
    def __init__(self, settings, *args, **kwargs) -> None:
        super().__init__(settings, *args, **kwargs)
        self.db_engine = DatabaseEngineFactory.create(self.settings)
        self.count: int = 0
        self.start_time = datetime.datetime.now()
        self.create_log_table()

    def create_log_table(self):
        self.db_engine.create_table(TushareIntegrationLog)

    def open_spider(self, spider):
        self.start_time = datetime.datetime.now()

    def close_spider(self, spider):
        description = ""
        model = spider.__model__
        if model:
            description = model.__table__.comment or ""

        log_entry = TushareIntegrationLog(
            batch_id=spider.settings.get("BATCH_ID", ''),
            spider_name=spider.name,
            description=description,
            count=self.count,
            start_time=self.start_time,
            end_time=datetime.datetime.now(),
        )
        self.db_engine.insert(
            TushareIntegrationLog,
            pd.DataFrame(
                [
                    {
                        'batch_id': log_entry.batch_id,
                        'spider_name': log_entry.spider_name,
                        'description': log_entry.description,
                        'count': log_entry.count,
                        'start_time': log_entry.start_time,
                        'end_time': log_entry.end_time,
                    }
                ]
            ),
        )

    def process_item(self, item, spider):
        self.count += len(item["data"])
        return item
