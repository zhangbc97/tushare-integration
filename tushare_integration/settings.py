# Scrapy settings for tushare_integration project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import functools
import logging
import os
import sys
from pathlib import Path
from typing import Annotated, Any, Dict, Literal

import pandas as pd
import requests
import yaml
from pydantic import BeforeValidator, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

point_frequency = [
    {'point': 120, 'frequency': 50},
    {'point': 2000, 'frequency': 200},
    {'point': 5000, 'frequency': 500},
    {'point': 10000, 'frequency': 1000},
]


def env_validator(key, case_sensitive=False):
    env_vars = {k.lower(): v for k, v in os.environ.items()} if not case_sensitive else os.environ
    key = key.lower() if not case_sensitive else key

    def validator(v):
        if key in env_vars:
            return env_vars[key]
        return v

    return validator


def env_variable(env_key, case_sensitive=False):
    return BeforeValidator(env_validator(env_key, case_sensitive))


class DatabaseConfig(BaseSettings):
    # 移除 db_type 字段
    # 添加 drivername 字段
    drivername: Annotated[str, env_variable('DB_DRIVER')] = Field(
        ..., description='数据库驱动名称，例如：clickhouse+native, mysql+pymysql'
    )

    host: Annotated[str, env_variable('DB_HOST')] = Field(..., description='数据库主机')
    port: Annotated[int, env_variable('DB_PORT')] = Field(..., description='数据库端口')
    user: Annotated[str, env_variable('DB_USER')] = Field(..., description='数据库用户名')
    password: Annotated[str, env_variable('DB_PASSWORD')] = Field('', description='数据库密码')

    db_name: Annotated[str, env_variable('DB_NAME')] = Field(..., description='数据库名称')
    template_params: dict[str, Any] = Field(default={}, description='SQL模板参数')

    # 移除 drivername property
    def get_uri(self):
        return f"{self.drivername}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"

    model_config = SettingsConfigDict(extra='ignore')


@functools.lru_cache(maxsize=1)
def get_tushare_point(token: str, url: str = "https://api.tushare.pro") -> int:
    """调用Tushare API获取用户积分

    Args:
        token: Tushare token
        url: Tushare API地址,默认为官方地址
    """
    try:
        response = requests.post(
            url=url,
            json={
                "api_name": "user",
                "token": token,
                "params": {"token": token},
            },
            headers={
                "Content-Type": "application/json",
            },
        )

        data = response.json()
        if data.get("code") == 0 and data.get("data", {}).get("items"):
            df = pd.DataFrame(data["data"]["items"], columns=data["data"]["fields"])
            total_points = int(df.iloc[:, 2].sum())
            return total_points
        logging.warning(f"获取Tushare积分失败,响应数据格式异常: {data}, 使用默认值2000")
        return 2000
    except Exception as e:
        logging.warning(f"获取Tushare积分失败: {e}, 使用默认值2000")
        return 2000


# 使用pydantic定义数据模型
class TushareIntegrationSettings(BaseSettings):
    # Tushare相关的配置项
    tushare_token: Annotated[str, env_variable('TUSHARE_TOKEN')] = Field(..., description='Tushare token')
    tushare_url: str = Field(default='https://api.tushare.pro', description='Tushare API URL')
    tushare_point: int = Field(default=2000, description='Tushare积分')

    # 目前接口有频次限制，暂时不从API获取积分，还是让用户手动设置积分
    # @model_validator(mode='after')
    # def get_point(self):
    #     """验证器: 从API获取积分"""
    #     # 获取token和url
    #     token = self.tushare_token
    #     url = self.tushare_url

    #     if token:  # 只有在有token的情况下才去获取积分
    #         self.tushare_point = get_tushare_point(token, url)
    #     return self

    tushare_max_concurrent_requests: int | None = Field(
        None, description='Tushare最大每分钟请求数,可手工指定，不指定会自动按积分计算'
    )

    database: DatabaseConfig = Field(..., description='数据库配置')

    reporters: list[str] = Field([], description='报告模块')
    feishu_webhook: Annotated[str, env_variable('FEISHU_WEBHOOK')] = Field(..., description='飞书webhook')

    parallel_mode: bool = Field(
        default=False, title='是否开启并行模式', description='并行模式下将会关闭自动依赖解析，用户需要自行处理任依赖'
    )
    batch_id: Annotated[str, env_variable('BATCH_ID')] = Field('', description='批次ID')

    bot_name: str = Field(default='tushare_integration', description='爬虫名称')
    spider_modules: list[str] = Field(default=['tushare_integration.spiders'], description='爬虫模块')
    newspider_module: str = Field(default='tushare_integration.spiders', description='新建爬虫目录')

    robotstxt_obey: bool = Field(default=False, description='是否遵守robots.txt')

    concurrent_requests: Annotated[int, env_variable('CONCURRENT_REQUESTS')] = Field(
        default=1, description='并发请求数'
    )
    concurrent_items: Annotated[int, env_variable('CONCURRENT_ITEMS')] = Field(default=100, description='并发item数')

    download_delay: float = Field(default=0, description='下载延')

    downloader_middlewares: dict[str, int | None] = Field(
        default={
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "tushare_integration.middlewares.TushareRetryDownloaderMiddleware": 543,
        },
        description='下载中间件',
    )

    retry_enabled: bool = Field(default=True, description='是否开启重试')
    retry_times: int = Field(default=10, description='重试次数')
    retry_delay: int = Field(default=10, description='重试延迟')

    templates_dir: str = Field(
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "spiders/templates"), description='模板目录'
    )

    item_pipelines: dict[str, int] = Field(
        default={
            "tushare_integration.pipelines.TushareIntegrationFillNAPipeline": 298,
            "tushare_integration.pipelines.TransformDTypePipeline": 299,
            "tushare_integration.pipelines.TushareIntegrationDataPipeline": 300,
            "tushare_integration.pipelines.RecordLogPipeline": 301,
        },
        description='item管道',
    )

    request_fingerprinter_implementation: str = Field(default='2.7', description='请求指纹实')
    twisted_reactor: str = Field(
        default='twisted.internet.asyncioreactor.AsyncioSelectorReactor', description='twisted反应堆'
    )
    reactor_threadpool_maxsize: int = Field(default=1, description='reactor线程池最大数量')
    feed_export_encoding: str = Field(default='utf-8', description='导出编码')

    closespider_errorcount: int = Field(default=1, description='错误数量')

    model_config = SettingsConfigDict(extra='ignore')

    def get_frequency(self):
        frequency = 0
        for freq in point_frequency:
            if self.tushare_point > freq['point']:
                frequency = freq['frequency']

        return frequency

    def get_settings(self):
        if not self.tushare_max_concurrent_requests:
            self.tushare_max_concurrent_requests = self.get_frequency()
        # 将所有key转为大写
        settings = {k.upper(): v for k, v in self.model_dump().items()}
        settings['DOWNLOAD_DELAY'] = 60 / settings["TUSHARE_MAX_CONCURRENT_REQUESTS"]
        return settings

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ):
        return env_settings, init_settings, file_secret_settings


def load_config(config_file: str | Path = 'config.yaml') -> TushareIntegrationSettings:
    """
    从指定的配置文件加载配置，并将配置项设置为全局变量

    Args:
        config_file: 配置文件路径，默认为 config.yaml

    Returns:
        配置项字典，所有配置项都已转换为大写

    Raises:
        SystemExit: 当配置文件无法读取时退出程序
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    except Exception as e:
        logging.error(f"无法读取配置文件 {config_file}: {e}")
        sys.exit(1)

    # 验证配置并获取设置
    settings = TushareIntegrationSettings.model_validate(config_data)

    # 将配置项设置为全局变量
    globals().update(settings.get_settings())

    return settings
