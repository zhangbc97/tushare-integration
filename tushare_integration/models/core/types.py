from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger as Integer
from sqlalchemy.types import Date, DateTime, Float, String


# String编译规则
@compiles(String, 'clickhouse')
def compile_string_clickhouse(element, compiler, **kw):
    return f'String' if element.length is None else f'String({element.length})'


@compiles(String, 'starrocks')
@compiles(String, 'doris')
@compiles(String, 'databend')
@compiles(String, 'mysql')
@compiles(String, 'duckdb')
def compile_string_others(element, compiler, **kw):
    length = element.length or 65535
    return f'VARCHAR({length})'


# Integer编译规则
@compiles(Integer, 'clickhouse')
def compile_integer_clickhouse(element, compiler, **kw):
    return 'Int64'


@compiles(Integer, 'starrocks')
@compiles(Integer, 'doris')
@compiles(Integer, 'databend')
@compiles(Integer, 'mysql')
@compiles(Integer, 'duckdb')
def compile_integer_others(element, compiler, **kw):
    return 'BIGINT'


# Float编译规则
@compiles(Float, 'clickhouse')
def compile_float_clickhouse(element, compiler, **kw):
    return 'Float64'


@compiles(Float, 'starrocks')
@compiles(Float, 'doris')
@compiles(Float, 'databend')
@compiles(Float, 'mysql')
@compiles(Float, 'duckdb')
def compile_float_others(element, compiler, **kw):
    return 'DOUBLE'


# Date编译规则
@compiles(Date, 'clickhouse')
def compile_date_clickhouse(element, compiler, **kw):
    return 'Date32'


@compiles(Date, 'starrocks')
@compiles(Date, 'doris')
@compiles(Date, 'databend')
@compiles(Date, 'mysql')
@compiles(Date, 'duckdb')
def compile_date_others(element, compiler, **kw):
    return 'DATE'


# DateTime编译规则
@compiles(DateTime, 'clickhouse')
def compile_datetime_clickhouse(element, compiler, **kw):
    return 'DateTime64'


@compiles(DateTime, 'starrocks')
@compiles(DateTime, 'doris')
@compiles(DateTime, 'databend')
@compiles(DateTime, 'mysql')
@compiles(DateTime, 'duckdb')
def compile_datetime_others(element, compiler, **kw):
    return 'DATETIME'
