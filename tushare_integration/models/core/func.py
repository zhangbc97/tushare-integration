from sqlalchemy.sql.functions import GenericFunction


# 定义自定义函数
class to_date(GenericFunction):
    name = 'to_date'
    identifier = 'to_date'

    # 为不同数据库定义编译规则
    type_map = {
        'mysql': 'to_date(%s)',
        'clickhouse': 'toDate(%s)',
        'starrocks': 'to_date(%s)',
        'doris': 'to_date(%s)',
        'databend': 'to_date(%s)',
        'duckdb': 'to_date(%s)',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def _compiler_dispatch(self):
        def compile_fn(compiler, **kw):
            dialect_name = compiler.dialect.name
            format_str = self.type_map.get(dialect_name, 'to_date(%s)')
            return format_str % compiler.process(self.clauses, **kw)

        return compile_fn
