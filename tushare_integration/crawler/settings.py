from typing import Dict, List, Type

from pydantic import BaseModel, ConfigDict, Field

from .middleware import Middleware
from .pipeline import Pipeline


class CrawlerSettings(BaseModel):
    """爬虫框架配置类"""

    model_config = ConfigDict(
        validate_assignment=True,  # 赋值时进行验证
        frozen=True,  # 创建后不可修改
    )

    # 并发配置
    concurrent_requests: int = Field(default=1, description="并发请求数", gt=0)
    concurrent_items: int = Field(default=100, description="并发处理的数据项数量", gt=0)

    # 重试配置
    retry_enabled: bool = Field(default=True, description="是否启用重试")
    retry_times: int = Field(default=3, description="最大重试次数", ge=0)
    retry_delay: int = Field(default=60, description="重试间隔(秒)", ge=0)

    # HTTP配置
    timeout: int = Field(default=30, description="请求超时时间(秒)", gt=0)
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")

    # 组件配置
    middlewares: List[Type[Middleware]] = Field(default_factory=list, description="中间件列表")
    pipelines: List[Type[Pipeline]] = Field(default_factory=list, description="管道列表")

    # 其他配置
    log_level: str = Field(default="INFO", description="日志级别", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
