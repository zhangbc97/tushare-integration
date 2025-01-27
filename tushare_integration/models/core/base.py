from typing import Any, ClassVar, Dict, List

from sqlalchemy.orm import DeclarativeBase


class TushareModelMixin(object):
    """Tushare 模型的混入类，包含所有 Tushare 相关的类属性"""

    __api_id__: ClassVar[int]
    __api_name__: ClassVar[str]
    __api_title__: ClassVar[str]
    __api_info_title__: ClassVar[str]
    __api_path__: ClassVar[List[str]]
    __api_path_ids__: ClassVar[List[int]]
    __api_points_required__: ClassVar[int]
    __api_special_permission__: ClassVar[bool]
    __has_vip__: ClassVar[bool]
    __dependencies__: ClassVar[List[str]]
    __primary_key__: ClassVar[List[str]]
    __start_date__: ClassVar[str | None]
    __end_date__: ClassVar[str | None]
    __api_params__: ClassVar[Dict[str, Any]]


class Base(DeclarativeBase, TushareModelMixin):
    """SQLAlchemy 声明性基类，包含了 Tushare 相关的所有属性"""

    ...
