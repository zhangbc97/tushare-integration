import typer
from rich.console import Console

from tushare_integration.manager import CrawlManager

console = Console()
run_app = typer.Typer(
    name='run',
    help='运行爬虫或任务',
    no_args_is_help=True
)


@run_app.command('job', help='运行预定义任务')
def run_job(job_name: str = typer.Argument(..., help='任务名称')):
    """运行预定义任务"""
    manager = CrawlManager()
    manager.run_job(job_name)


@run_app.command('spider', help='运行指定爬虫')
def run_spider(
    spider: str = typer.Argument(
        ...,
        help='爬虫名称（支持通配符）',
    )
):
    """运行指定爬虫"""
    manager = CrawlManager()
    manager.run_spider(spider) 