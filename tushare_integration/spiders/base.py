import json
import logging
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from typing import Any, ClassVar, Dict, Generator, Iterator, Optional

import httpx
import pandas as pd
from sqlalchemy import Column

from tushare_integration.db_engine import DBEngine
from tushare_integration.models.core.base import Base
from tushare_integration.settings import TushareIntegrationSettings


class BaseSpider(ABC):
    """
    爬虫基类，负责控制整个采集流程
    """

    __spider_name__: str = ""
    __model__: ClassVar[type[Base]] = Base  # 数据模型类
    custom_settings: Dict[str, Any] = {}  # 自定义设置
    _last_request_time: float = 0  # 上次请求时间

    def __init__(
        self,
        settings: TushareIntegrationSettings,
    ):
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self._executor: Optional[ThreadPoolExecutor] = None
        self.client = httpx.Client(timeout=settings.timeout, headers=settings.headers)
        self.db_engine = DBEngine(settings)  # type: ignore

    @property
    def api_name(self) -> str:
        """API名称"""
        return getattr(self.__model__, '__api_name__', self.__spider_name__)

    @property
    def table_name(self) -> str:
        """数据表名称"""
        return getattr(self.__model__, '__tablename__', self.__spider_name__)

    @property
    def start_date(self) -> str | None:
        """起始日期"""
        return getattr(self.__model__, '__start_date__', None)

    @property
    def fields(self) -> str:
        """字段列表"""
        if hasattr(self.__model__, '__table__'):
            return ",".join([column.name for column in self.__model__.__table__.columns])
        return ""

    def middleware_throttling(self) -> None:
        """请求频率限制中间件"""
        now = time.time()
        wait = (1.0 / self.settings.concurrent_requests) - (now - self._last_request_time)
        if wait > 0:
            self.logger.debug(f"Request frequency too high, waiting {wait:.2f}s")
            time.sleep(wait)
        self._last_request_time = now

    def middleware_check_response(self, response: httpx.Response) -> None:
        """检查响应是否符合要求

        Args:
            response: 响应对象

        Raises:
            ValueError: 响应格式错误
            RuntimeError: API返回错误
        """
        try:
            resp_data = response.json()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON response: {response.text[:100]}")

        if not isinstance(resp_data, dict):
            raise ValueError(f"Response data is not a dict: {resp_data}")

        # 检查必要字段
        required_fields = ["code", "data"]
        for field in required_fields:
            if field not in resp_data:
                raise ValueError(f"Response missing '{field}' field: {resp_data}")

        # 检查返回码
        code = resp_data["code"]
        if code != 0:
            msg = resp_data.get("msg", "unknown error")
            raise RuntimeError(f"API error: code={code}, msg={msg}")

        # 检查data字段结构
        data = resp_data["data"]
        if not isinstance(data, dict):
            raise ValueError(f"Response data field is not a dict: {data}")

        # 检查data中的必要字段
        data_required_fields = ["fields", "items"]
        for field in data_required_fields:
            if field not in data:
                raise ValueError(f"Response data missing '{field}' field: {data}")

    def request(self, request: httpx.Request) -> httpx.Response | None:
        """发送请求并处理重试逻辑

        Args:
            request: 要发送的请求对象

        Returns:
            处理后的响应

        Raises:
            RuntimeError: 达到最大重试次数时抛出
            Exception: 其他请求失败的情况
        """
        max_retries = self.settings.retry_times

        for retry in range(max_retries + 1):
            try:
                # 频率限制
                self.middleware_throttling()
                response = self.client.send(request)
                # 检查响应
                self.middleware_check_response(response)
                return response

            except Exception as e:
                self.logger.warning(f"Request failed: {e}, retry {retry + 1}")
                if retry == max_retries:
                    self.logger.error(f"Request failed after {max_retries} retries")
                    raise
                time.sleep(self.settings.retry_delay)

    def run(self):
        """运行爬虫"""
        try:
            with ThreadPoolExecutor(max_workers=self.settings.concurrent_requests) as executor:
                self._executor = executor
                futures = []
                for request in self.start_requests():
                    futures.append(executor.submit(self._process_request, request))

                # 等待所有任务完成
                for future in futures:
                    future.result()  # 这会重新抛出任务中的异常
        finally:
            self._executor = None
            self.client.close()

    def _process_request(self, request: httpx.Request) -> None:
        """处理单个请求的工作函数"""
        try:
            if response := self.request(request):
                for item in self.parse(response):
                    self.process_item(item)  # 使用新的 process_item 方法
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")

    def stop(self):
        """停止爬虫"""
        if self._executor is not None:
            self._executor.shutdown(wait=False)

    @abstractmethod
    def start_requests(self) -> Iterator[httpx.Request]:
        """生成初始请求"""
        raise NotImplementedError

    @abstractmethod
    def parse(self, response: httpx.Response) -> Generator[pd.DataFrame, None, None]:
        """解析响应

        Args:
            response: 响应对象

        Yields:
            pd.DataFrame: 解析后的数据
        """
        raise NotImplementedError

    def process_item(self, item: pd.DataFrame) -> pd.DataFrame:
        """处理数据项，按顺序执行所有pipeline处理

        Args:
            item: 包含数据的DataFrame

        Returns:
            处理后的DataFrame
        """
        if not isinstance(item, pd.DataFrame):
            raise TypeError(f"Expected pd.DataFrame, got {type(item)}")

        if item.empty:
            return item

        item = self.pipeline_fill_na(item)
        item = self.pipeline_transform_dtype(item)
        item = self.pipeline_save_data(item)
        item = self.pipeline_record_log(item)
        return item

    def _get_default_by_column(self, column: Column):
        """获取列的默认值"""
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

    def pipeline_fill_na(self, data: pd.DataFrame) -> pd.DataFrame:
        """填充缺失值"""
        for column in self.__model__.__table__.columns:
            default = column.default.arg if column.default else self._get_default_by_column(column)  # type: ignore
            # 需要特殊处理NaT,Pandas的fillna方法不支持NaT
            data[column.name] = data[column.name].replace({pd.NaT: None}).fillna(default)
        return data

    def pipeline_transform_dtype(self, data: pd.DataFrame) -> pd.DataFrame:
        """转换数据类型"""
        for column in self.__model__.__table__.columns:
            python_type = column.type.python_type
            type_name = python_type.__name__
            try:
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
            except Exception as e:
                self.logger.warning(f"转换列 {column.name} 类型失败: {e}")
        return data

    def pipeline_save_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """数据持久化"""
        if not data.empty:
            model = self.__model__
            if model.__primary_key__:
                data = data.drop_duplicates(subset=model.__primary_key__, keep="last")
                self.db_engine.upsert(model, data=data)
            else:
                self.logger.debug(f"Insert data into {self.table_name}, data count: {len(data)}")
                self.db_engine.insert(model, data=data)
        return data

    def pipeline_record_log(self, data: pd.DataFrame) -> pd.DataFrame:
        """记录日志"""
        if not data.empty:
            self.logger.info(f"Successfully processed {len(data)} records for {self.__spider_name__}")
        return data

    def get_request(self, params: dict | None = None, meta: dict | None = None) -> httpx.Request:
        """生成请求对象

        Args:
            params: 请求参数
            meta: 请求元数据

        Returns:
            httpx.Request: 请求对象
        """
        if params is None:
            params = {}
        if meta is None:
            meta = {}

        self.logger.debug(f"Generating request for {self.api_name} with params: {params}")

        # 构建请求体
        body = {
            "api_name": self.api_name,
            "token": self.settings.tushare_token,
            "params": params,
            "fields": self.fields,
        }

        # 构建请求对象
        request = httpx.Request(
            method="POST",
            url=self.settings.tushare_url,
            json=body,
            headers={
                "Content-Type": "application/json",
            },
            extensions={'meta': {'api_name': self.api_name, 'params': params, **meta}},
        )

        return request

    def parse_response(self, response: httpx.Response) -> pd.DataFrame:
        """解析响应数据

        Args:
            response: 响应对象

        Returns:
            pd.DataFrame: 解析后的数据

        Raises:
            RuntimeError: API返回错误
        """
        resp = response.json()

        if resp["code"] != 0:
            raise RuntimeError(f"API error: code={resp['code']}, msg={resp.get('msg', 'unknown error')}")

        data = resp["data"]
        if not data["items"]:
            return pd.DataFrame()

        return pd.DataFrame(data=data["items"], columns=data["fields"])
