import typer

from tushare_integration.manager import CrawlManager

try:
    from rich import print
except ImportError:
    pass

crawl_app = typer.Typer(name='CrawlManager', help='CrawlManager help', no_args_is_help=True)

query_app = typer.Typer(
    name='QueryManager',
    help='QueryManager help',
    no_args_is_help=True,
)


@query_app.command('list', help="List spiders")
def list_spiders():
    manager = CrawlManager()
    print(manager.list_spiders())


@crawl_app.command('job', help="Run a job", no_args_is_help=True)
def run_job(job_name: str = typer.Argument(..., help="Name of the job to run")):
    manager = CrawlManager()
    manager.run_job(job_name)


@crawl_app.command('spider', help="Run spiders", no_args_is_help=True)
def run_spider(
    spider: str = typer.Argument(
        ...,
        help="Wildcard of the spider to run",
    )
):
    manager = CrawlManager()
    manager.run_spider(spider)
