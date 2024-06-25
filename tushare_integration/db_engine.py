import clickhouse_connect.dbapi
import jinja2
import pandas as pd
from sqlalchemy import create_engine, text

from tushare_integration.settings import TushareIntegrationSettings


class DBEngine(object):
    def __init__(self, settings: TushareIntegrationSettings):
        self.settings = settings
        self.templates = {
            'create': jinja2.Template(
                open(
                    f'tushare_integration/schema/template/{self.settings.database.db_type.lower()}/table.jinja2'
                ).read()
            ),
            'insert': jinja2.Template(
                open(
                    f'tushare_integration/schema/template/{self.settings.database.db_type.lower()}/insert.jinja2'
                ).read()
            ),
            'upsert': jinja2.Template(
                open(
                    f'tushare_integration/schema/template/{self.settings.database.db_type.lower()}/upsert.jinja2'
                ).read()
            ),
        }

        self.functions = {
            'to_date': 'to_date',
        }

    def insert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        raise NotImplementedError

    def upsert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        raise NotImplementedError

    def create_table(self, table_name: str, schema: dict) -> None:
        raise NotImplementedError

    def query_df(self, sql: str) -> pd.DataFrame:
        raise NotImplementedError

    def query(self, sql: str) -> pd.DataFrame:
        raise NotImplementedError


class SQLAlchemyEngine(DBEngine):
    def __init__(self, settings: TushareIntegrationSettings):
        super().__init__(settings)
        self.conn = create_engine(self.settings.database.get_uri()).connect()

    def insert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        sql = self.templates['insert'].render(
            db_name=self.settings.database.db_name,
            table_name=table_name,
            columns=data.columns.tolist(),
            template_params=self.settings.database.template_params,
        )

        self.conn.execute(statement=text(sql), parameters=data.to_dict('records'))  # type: ignore

    def upsert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        sql = self.templates['upsert'].render(
            db_name=self.settings.database.db_name,
            table_name=table_name,
            columns=data.columns.tolist(),
            primary_key=schema.get('primary_key', []),
            template_params=self.settings.database.template_params,
        )
        self.conn.execute(statement=text(sql), parameters=data.to_dict('records'))  # type: ignore

    def create_table(self, table_name: str, schema: dict) -> None:
        self.conn.execute(
            statement=text(
                self.templates['create'].render(
                    db_name=self.settings.database.db_name,
                    table_name=table_name,
                    **schema,
                    template_params=self.settings.database.template_params,
                )
            )
        )

    def query_df(self, sql: str) -> pd.DataFrame:
        return pd.read_sql(sql, self.conn)

    def query(self, sql: str):
        return self.conn.execute(statement=text(sql))


class MySQLEngine(SQLAlchemyEngine):
    def __init__(self, settings: TushareIntegrationSettings):
        super().__init__(settings)
        self.functions['to_date'] = 'Date'


class ApacheDorisEngine(SQLAlchemyEngine):
    def __init__(self, settings: TushareIntegrationSettings):
        super().__init__(settings)
        self.functions['to_date'] = 'to_date'


class ClickhouseEngine(DBEngine):
    def __init__(self, settings: TushareIntegrationSettings):
        super().__init__(settings)

        self.client = clickhouse_connect.get_client(
            host=settings.database.host,
            port=settings.database.port,
            username=settings.database.user,
            password=settings.database.password,
            database=settings.database.db_name,
        )

        self.functions['to_date'] = 'toDate'

    def insert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        self.client.insert_df(table_name, data)

    def upsert(self, table_name: str, schema: dict, data: pd.DataFrame) -> None:
        self.client.insert_df(table_name, data)

    def create_table(self, table_name: str, schema: dict) -> None:
        self.client.query(
            self.templates['create'].render(
                db_name=self.settings.database.db_name,
                table_name=table_name,
                **schema,
                template_params=self.settings.database.template_params,
            )
        )

    def query_df(self, sql: str) -> pd.DataFrame:
        return self.client.query_df(sql)

    def query(self, sql: str):
        return self.client.query(sql)


class DatabaseEngineFactory(object):
    @staticmethod
    def create(settings: TushareIntegrationSettings) -> DBEngine:
        if settings.database.db_type == 'clickhouse':
            return ClickhouseEngine(settings)
        elif settings.database.db_type == 'doris':
            return ApacheDorisEngine(settings)
        elif settings.database.db_type == 'mysql':
            return MySQLEngine(settings)
        else:
            raise NotImplementedError
