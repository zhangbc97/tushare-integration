from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import FunctionElement


# 定义自定义函数
class to_date(FunctionElement):
    name = 'to_date'


# 为MySQL编译器定义
@compiles(to_date, 'mysql')
def compile_to_date_mysql(element, compiler, **kw):
    return "to_date(%s)" % compiler.process(element.clauses)


# 为ClickHouse编译器定义
@compiles(to_date, 'clickhouse')
def compile_to_date_clickhouse(element, compiler, **kw):
    return "toDate(%s)" % compiler.process(element.clauses)


@compiles(to_date, 'starrocks')
def compile_to_date_starrocks(element, compiler, **kw):
    return "to_date(%s)" % compiler.process(element.clauses)


@compiles(to_date, 'doris')
def compile_to_date_doris(element, compiler, **kw):
    return "to_date(%s)" % compiler.process(element.clauses)
