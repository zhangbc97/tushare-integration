import os

import jinja2


class SQLTemplate(object):
    def __init__(self, db_type: str = 'databend'):
        self.db_type = db_type

    def render(self, db_name: str, table_name: str, template_file: str, **kwargs):
        if not os.path.exists(f"tushare_integration/schema/template/{self.db_type}/{template_file}"):
            raise FileNotFoundError(f"tushare_integration/schema/template/{self.db_type}/{template_file}")

        with open(f"tushare_integration/schema/template/{self.db_type}/{template_file}", "r", encoding="utf-8") as f:
            template = jinja2.Template(f.read())
            sql = template.render(
                db_name=db_name,
                table_name=table_name,
                **kwargs
            )
            return sql

    def create_table(self, db_name: str, table_name: str, schema: dict):
        return self.render(db_name, table_name, "table.jinja2", **schema)

    def insert_data(self, db_name: str, table_name: str, columns: list):
        return self.render(db_name, table_name, "insert.jinja2", columns=columns)

    def upsert_data(self, db_name: str, table_name: str, columns: list, duplicate_keys: str):
        return self.render(db_name, table_name, "upsert.jinja2", columns=columns, duplicate_keys=duplicate_keys)
