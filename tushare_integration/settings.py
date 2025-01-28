import functools
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Annotated, Any, Dict, Literal

import pandas as pd
import requests
import yaml
from pydantic import BeforeValidator, Field, field_validator
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

    tushare_max_concurrent_requests: int | None = Field(
        None, description='Tushare最大每分钟请求数,可手工指定，不指定会自动按积分计算'
    )

    database: DatabaseConfig = Field(..., description='数据库配置')

    reporters: list[str] = Field([], description='报告模块')
    feishu_webhook: Annotated[str, env_variable('FEISHU_WEBHOOK')] = Field(default='', description='飞书webhook')

    parallel_mode: bool = Field(
        default=False, title='是否开启并行模式', description='并行模式下将会关闭自动依赖解析，用户需要自行处理任依赖'
    )

    batch_id: Annotated[str, env_variable('BATCH_ID')] = Field(
        default_factory=lambda: uuid.uuid1().hex, description='批次ID'
    )

    concurrent_spiders: Annotated[int, env_variable('CONCURRENT_SPIDERS')] = Field(default=1, description='并发爬虫数')

    download_delay: float = Field(default=0, description='下载延迟')

    max_requests_per_minute: int = Field(default=60, description='每分钟最大请求数')
    retry_enabled: bool = Field(default=True, description='是否开启重试')
    retry_times: int = Field(default=10, description='重试次数')
    retry_delay: int = Field(default=10, description='重试延迟')

    timeout: int = Field(default=30, description="请求超时时间(秒)", gt=0)
    headers: Dict[str, str] = Field(
        default={"User-Agent": "tushare-integration"},
        description="请求头",
    )

    # 日志配置
    log_level: Annotated[Literal['DEBUG', 'INFO', 'WARNING', 'ERROR'], env_variable('LOG_LEVEL')] = Field(
        default='INFO', description='日志级别(DEBUG/INFO/WARNING/ERROR)'
    )

    model_config = SettingsConfigDict(extra='ignore')

    def get_frequency(self):
        frequency = 0
        for freq in point_frequency:
            if self.tushare_point > freq['point']:
                frequency = freq['frequency']

        return frequency

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

    @field_validator('batch_id')
    def validate_batch_id(cls, v: str) -> str:
        return v if v else uuid.uuid1().hex

    @classmethod
    def load_config(cls, config_file: str | Path = 'config.yaml') -> 'TushareIntegrationSettings':
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
        settings = cls.model_validate(config_data)

        return settings
