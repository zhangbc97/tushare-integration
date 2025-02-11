from sqlalchemy import schema as sa_schema
from sqlalchemy.sql import sqltypes
from starrocks.dialect import StarRocksDDLCompiler, StarRocksDialect


class TSStarRocksDDLCompiler(StarRocksDDLCompiler):
    def post_create_table(self, table):
        """Build table-level CREATE options like ENGINE and COLLATE."""

        table_opts = []

        opts = dict(
            (k[len(self.dialect.name) + 1 :].upper(), v)
            for k, v in table.kwargs.items()
            if k.startswith("%s_" % self.dialect.name)
        )

        if table.comment is not None:
            opts["COMMENT"] = table.comment

        if 'ENGINE' in opts:
            table_opts.append(f'ENGINE={opts["ENGINE"]}')

        if 'PRIMARY_KEY' in opts:
            table_opts.append(f'PRIMARY KEY({opts["PRIMARY_KEY"]})')

        if 'DISTRIBUTED_BY' in opts:
            table_opts.append(f'DISTRIBUTED BY HASH({opts["DISTRIBUTED_BY"]})')

        if 'PARTITION_BY' in opts:
            partition_type = opts.get('PARTITION_TYPE', 'RANGE')  # Default to RANGE partition
            table_opts.append(f'PARTITION BY {partition_type}({opts["PARTITION_BY"]})')

            # Handle partition definitions if provided
            if 'PARTITION_DESC' in opts:
                table_opts.append(opts["PARTITION_DESC"])

        if 'ORDER_BY' in opts:
            table_opts.append(f'ORDER BY ({opts["ORDER_BY"]})')

        if "COMMENT" in opts:
            comment = self.sql_compiler.render_literal_value(opts["COMMENT"], sqltypes.String())
            table_opts.append(f"COMMENT {comment}")

        # ToDo - Partition
        # ToDo - Distribution
        # ToDo - Order by

        if "PROPERTIES" in opts:
            props = ",\n".join([f'\t"{k}"="{v}"' for k, v in opts["PROPERTIES"]])
            table_opts.append(f"PROPERTIES(\n{props}\n)")

        return " ".join(table_opts)

    def get_column_specification(self, column, **kw):
        """Builds column DDL."""

        colspec = [
            self.preparer.format_column(column),
            self.dialect.type_compiler.process(column.type, type_expression=column),
        ]

        # ToDo: Support aggregation type
        #  agg_type: aggregation type.If not specified, this column is key column.If specified, it is value
        #  column.The aggregation types supported are as follows:
        #  SUM, MAX, MIN, REPLACE
        #  HLL_UNION(only for HLL type)
        #  BITMAP_UNION(only for BITMAP)
        #  REPLACE_IF_NOT_NULL

        # if column.computed is not None:
        #     colspec.append(self.process(column.computed))

        # is_timestamp = isinstance(
        #     column.type._unwrapped_dialect_impl(self.dialect),
        #     sqltypes.TIMESTAMP,
        # )

        if not column.nullable:
            colspec.append("NOT NULL")

        # see: https://docs.sqlalchemy.org/en/latest/dialects/mysql.html#mysql_timestamp_null  # noqa
        # elif column.nullable and is_timestamp:
        #     colspec.append("NULL")

        # ToDo >= version 3.0
        if (
            column.table is not None
            and column is column.table._autoincrement_column
            and (column.server_default is None or isinstance(column.server_default, sa_schema.Identity))
            and not (
                self.dialect.supports_sequences
                and isinstance(column.default, sa_schema.Sequence)
                and not column.default.optional
            )
        ):
            colspec[1] = "BIGINT"  # ToDo - remove this, find way to fix the test
            colspec.append("AUTO_INCREMENT")
        else:
            default = self.get_column_default_string(column)
            if default is not None:
                colspec.append("DEFAULT " + default)
        # Column comment is not supported in Starrocks
        comment = column.comment
        if comment is not None:
            literal = self.sql_compiler.render_literal_value(comment, sqltypes.String())
            colspec.append("COMMENT " + literal)

        return " ".join(colspec)


StarRocksDialect.ddl_compiler = TSStarRocksDDLCompiler
