import os

import jinja2

from tushare_integration.settings import TushareIntegrationSettings


class SQLTemplate(object):
    def __init__(self, settings: TushareIntegrationSettings):
        self.settings = settings
        self.db_type = self.settings.db_type

    def render(self, table_name: str, template_file: str, **kwargs):
        if not os.path.exists(f"tushare_integration/schema/template/{self.db_type}/{template_file}"):
            raise FileNotFoundError(f"tushare_integration/schema/template/{self.db_type}/{template_file}")

        with open(f"tushare_integration/schema/template/{self.db_type}/{template_file}", "r", encoding="utf-8") as f:
            template = jinja2.Template(f.read())
            sql = template.render(
                db_name=self.settings.db_name,
                table_name=table_name,
                **kwargs
            )
            return sql

    def create_table(self, table_name: str, schema: dict):
        return self.render(table_name, "table.jinja2", **schema, template_params=self.settings.template_params)

    def insert_data(self, table_name: str, columns: list):
        return self.render(table_name, "insert.jinja2", columns=columns, template_params=self.settings.template_params)

    def upsert_data(self, table_name: str, columns: list, duplicate_keys: str):
        return self.render(table_name, "upsert.jinja2", columns=columns, duplicate_keys=duplicate_keys,
                           template_params=self.settings.template_params)
