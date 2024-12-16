import typer
from rich.console import Console
from rich.table import Table

from tushare_integration.manager import CrawlManager

console = Console()

crawl_app = typer.Typer(name='CrawlManager', help='CrawlManager help', no_args_is_help=True)

query_app = typer.Typer(
    name='QueryManager',
    help='QueryManager help',
    no_args_is_help=True,
)


@query_app.command('list', help="List spiders")
def list_spiders():
    manager = CrawlManager()
    spiders_info = manager.list_spiders()

    # 按路径排序
    spiders_info.sort(key=lambda x: x['api_path'])

    # 创建表格
    table = Table(title="Spider列表")

    # 添加列 - 更新了颜色样式
    table.add_column("名称", style="bright_green")  # 改为亮绿色
    table.add_column("接口", style="bright_blue")  # 改为亮蓝色
    table.add_column("路径", style="bright_yellow")  # 改为亮黄色

    # 添加行
    for spider in spiders_info:
        table.add_row(spider['api_title'], spider['name'], spider['api_path'])

    # 打印表格
    console.print(table)


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
