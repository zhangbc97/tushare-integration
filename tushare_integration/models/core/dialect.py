from sqlalchemy import exc
from sqlalchemy import schema as sa_schema
from sqlalchemy import util
from sqlalchemy.sql import sqltypes

try:
    from databend_sqlalchemy.databend_dialect import DatabendDDLCompiler, DatabendDialect

    class TSDatabendDDLCompiler(DatabendDDLCompiler):

        def post_create_table(self, table):
            table_opts = []
            db_opts = table.dialect_options["databend"]

            engine = db_opts.get("engine")
            if engine is not None:
                table_opts.append(f" ENGINE={engine}")

            cluster_keys = db_opts.get("cluster_by")
            if cluster_keys is not None:
                if isinstance(cluster_keys, str):
                    cluster_by = cluster_keys
                elif isinstance(cluster_keys, list):
                    cluster_by = ", ".join(
                        self.sql_compiler.process(
                            expr if not isinstance(expr, str) else table.c[expr],
                            include_table=False,
                            literal_binds=True,
                        )
                        for expr in cluster_keys
                    )
                else:
                    cluster_by = ""
                table_opts.append(f"\n CLUSTER BY ( {cluster_by} )")

            if table.comment is not None:
                comment = self.sql_compiler.render_literal_value(table.comment, sqltypes.String())
                table_opts.append(f" COMMENT={comment}")

            # ToDo - Engine options

            return " ".join(table_opts)

        def get_column_specification(self, column, **kwargs):
            spec = super().get_column_specification(column, **kwargs)

            if column.comment is not None:
                spec += f" COMMENT {self.sql_compiler.render_literal_value(column.comment, sqltypes.String())}"

            return spec

    DatabendDialect.ddl_compiler = TSDatabendDDLCompiler

except:
    pass

try:
    from starrocks.dialect import StarRocksDDLCompiler, StarRocksDialect

    class TSStarRocksDDLCompiler(StarRocksDDLCompiler):

        def visit_create_table(self, create, **kw):
            table = create.element
            preparer = self.preparer

            text = "\nCREATE "
            if table._prefixes:
                text += " ".join(table._prefixes) + " "

            text += "TABLE "
            if create.if_not_exists:
                text += "IF NOT EXISTS "

            text += preparer.format_table(table) + " "

            create_table_suffix = self.create_table_suffix(table)
            if create_table_suffix:
                text += create_table_suffix + " "

            text += "("

            separator = "\n"

            # Sort columns to put primary key columns first
            pk_cols = []
            opts = dict(
                (k[len(self.dialect.name) + 1 :].upper(), v)
                for k, v in table.kwargs.items()
                if k.startswith("%s_" % self.dialect.name)
            )
            if 'PRIMARY_KEY' in opts:
                pk_cols = [col.strip() for col in opts['PRIMARY_KEY'].split(',')]

            # Sort columns list while preserving primary key order
            sorted_columns = []
            remaining_columns = []
            column_map = {col.element.name: col for col in create.columns}

            # First add primary key columns in their specified order
            for pk_col in pk_cols:
                if pk_col in column_map:
                    sorted_columns.append(column_map[pk_col])

            # Then add remaining columns
            for create_column in create.columns:
                if create_column.element.name not in pk_cols:
                    remaining_columns.append(create_column)

            sorted_columns.extend(remaining_columns)

            # Process columns in the new order
            first_pk = False
            for create_column in sorted_columns:
                column = create_column.element
                try:
                    processed = self.process(create_column, first_pk=column.primary_key and not first_pk)
                    if processed is not None:
                        text += separator
                        separator = ", \n"
                        text += "\t" + processed
                    if column.primary_key:
                        first_pk = True
                except exc.CompileError as ce:
                    util.raise_(  # type: ignore
                        exc.CompileError(
                            util.u("(in table '%s', column '%s'): %s") % (table.description, column.name, ce.args[0])  # type: ignore
                        ),
                        from_=ce,
                    )

            text += "\n)%s\n\n" % self.post_create_table(table)
            return text

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

            if "COMMENT" in opts:
                comment = self.sql_compiler.render_literal_value(opts["COMMENT"], sqltypes.String())
                table_opts.append(f"COMMENT {comment}")

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
except:
    pass

try:
    from duckdb_engine import Dialect
except:
    pass
