# Scrapy settings for tushare_integration project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os
from typing import Literal

import yaml
from pydantic import Field, Extra, ConfigDict
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

point_frequency = [
    {'point': 120, 'frequency': 50},
    {'point': 2000, 'frequency': 200},
    {'point': 5000, 'frequency': 500},
    {'point': 10000, 'frequency': 1000}
]


class DatabaseConfig(BaseSettings):
    # 数据库相关配置
    db_type: Literal["clickhouse", "mysql", "databend"] = Field(..., env="DB_TYPE", description='SQL模板')

    host: str = Field(..., env='DB_HOST', description='数据库主机')
    port: int = Field(..., env='DB_PORT', description='数据库端口')
    user: str = Field(..., env='DB_USER', description='数据库用户名')
    password: str = Field('', env='DB_PASSWORD', description='数据库密码')

    db_name: str = Field(..., env='DB_NAME', description='数据库名称')
    template_params: dict[str, str] = Field(default={}, description='SQL模板参数')

    def get_uri(self):
        if self.db_type == 'clickhouse':
            return f"clickhouse://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.db_type == 'mysql':
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        elif self.db_type == 'databend':
            return f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"
        else:
            raise ValueError(f"Unsupported db_type: {self.db_type}")


# 使用pydantic定义数据模型
class TushareIntegrationSettings(BaseSettings):
    # Tushare相关的配置项
    tushare_token: str = Field(..., env="TUSHARE_TOKEN", description='Tushare token')
    tushare_url: str = Field('https://api.tushare.pro', description='Tushare API URL')
    tushare_point: int = Field(2000, env='TUSHARE_POINT', description='Tushare积分')
    tushare_max_concurrent_requests: int | None = Field(None,
                                                        description='Tushare最大每分钟请求数,可手工指定，不指定会自动按积分计算')

    database: DatabaseConfig = Field(..., description='数据库配置')

    reporters: list[str] = Field([], description='报告模块')
    feishu_webhook: str = Field(..., env='FEISHU_WEBHOOK', description='飞书webhook')

    batch_id: str = Field('', env='BATCH_ID', description='批次ID')

    bot_name: str = Field(default='tushare_integration', description='爬虫名称')
    spider_modules: list[str] = Field(default=['tushare_integration.spiders'], description='爬虫模块')
    newspider_module: str = Field(default='tushare_integration.spiders', description='新建爬虫目录')

    robotstxt_obey: bool = Field(default=False, description='是否遵守robots.txt')

    concurrent_requests: int = Field(default=1, env="CONCURRENT_REQUESTS", description='并发请求数')
    concurrent_items: int = Field(default=100, env="CONCURRENT_ITEMS", description='并发item数')

    download_delay: float = Field(default=0, description='下载延迟')

    downloader_middlewares: dict[str, int | None] = Field(default={
        "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        "tushare_integration.middlewares.TushareRetryDownloaderMiddleware": 543,
    }, description='下载中间件')

    retry_enabled: bool = Field(default=True, description='是否开启重试')
    retry_times: int = Field(default=6, description='重试次数')
    retry_delay: int = Field(default=10, description='重试延迟')

    templates_dir: str = Field(default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "spiders/templates"
    ), description='模板目录')

    item_pipelines: dict[str, int] = Field(default={
        "tushare_integration.pipelines.TushareIntegrationFillNAPipeline": 298,
        "tushare_integration.pipelines.TransformDTypePipeline": 299,
        "tushare_integration.pipelines.TushareIntegrationDataPipeline": 300,
        "tushare_integration.pipelines.RecordLogPipeline": 301,
    }, description='item管道')

    request_fingerprinter_implementation: str = Field(default='2.7', description='请求指纹实现')
    twisted_reactor: str = Field(default='twisted.internet.asyncioreactor.AsyncioSelectorReactor',
                                 description='twisted反应堆')
    reactor_threadpool_maxsize: int = Field(default=1, description='reactor线程池最大数量')
    feed_export_encoding: str = Field(default='utf-8', description='导出编码')

    closespider_errorcount: int = Field(default=1, description='错误数量')

    model_config = ConfigDict(extra=Extra.allow)

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
    def settings_customise_sources(cls, settings_cls: type[BaseSettings], init_settings: PydanticBaseSettingsSource,
                                   env_settings: PydanticBaseSettingsSource,
                                   dotenv_settings: PydanticBaseSettingsSource,
                                   file_secret_settings: PydanticBaseSettingsSource):
        return env_settings, init_settings, file_secret_settings


# 保持scrapy兼容
for key, value in TushareIntegrationSettings.model_validate(
        yaml.safe_load(open('config.yaml', 'r', encoding='utf-8').read())
).get_settings().items():
    locals()[key] = value
