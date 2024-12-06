from typing import Optional

from clickhouse_sqlalchemy.types import Date32, DateTime64, Float64, Int64
from sqlalchemy.types import BigInteger
from sqlalchemy.types import Date as SADate
from sqlalchemy.types import DateTime as SADateTime
from sqlalchemy.types import Double as SADouble
from sqlalchemy.types import Float as SAFloat
from sqlalchemy.types import String as SAString
from sqlalchemy.types import TypeDecorator, TypeEngine

# 受支持的数据库
# clickhouse
# doris
# starrocks
# mysql
# 除了clickhouse外，doris、starrocks和mysql基本兼容


class String(TypeDecorator):
    """字符串类型"""

    impl = SAString
    cache_ok = True

    def __init__(self, length: Optional[int] = None):
        super().__init__(length=length if length else 255)
        self.length = length

    def load_dialect_impl(self, dialect) -> TypeEngine:
        match dialect.name:
            case 'clickhouse':
                return dialect.type_descriptor(SAString(self.length))
            case 'starrocks' | 'doris':
                return dialect.type_descriptor(SAString(self.length or 65535))
            case _:
                return dialect.type_descriptor(SAString(self.length or 255))

    @property
    def python_type(self):
        return str


class Integer(TypeDecorator):
    """整数类型"""

    impl = BigInteger
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:
        match dialect.name:
            case 'clickhouse':
                return dialect.type_descriptor(Int64())
            case _:
                return dialect.type_descriptor(BigInteger())

    @property
    def python_type(self):
        return int


class Float(TypeDecorator):
    """浮点数类型"""

    impl = SAFloat
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:
        match dialect.name:
            case 'clickhouse':
                return dialect.type_descriptor(Float64())
            case _:
                return dialect.type_descriptor(SADouble())

    @property
    def python_type(self):
        return float


class Date(TypeDecorator):
    """日期类型"""

    impl = SADate
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:
        match dialect.name:
            case 'clickhouse':
                return dialect.type_descriptor(Date32())
            case _:
                return dialect.type_descriptor(SADate())

    @property
    def python_type(self):
        return str


class DateTime(TypeDecorator):
    """日期时间类型"""

    impl = SADateTime
    cache_ok = True

    def load_dialect_impl(self, dialect) -> TypeEngine:
        match dialect.name:
            case 'clickhouse':
                return dialect.type_descriptor(DateTime64())
            case _:
                return dialect.type_descriptor(SADateTime())

    @property
    def python_type(self):
        return str
