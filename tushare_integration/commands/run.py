from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from tushare_integration.manager import CrawlManager

console = Console()
run_app = typer.Typer(name='run', help='运行爬虫或任务', no_args_is_help=True)


@run_app.command('job', help='运行预定义任务')
def run_job(
    job_name: str = typer.Option(None, '--job', '-j', help='任务名称，例如：daily_update'),
    job_file: Path = typer.Option(None, '--job-file', '-f', help='任务配置文件路径，例如：jobs.yaml'),
    config: Path = typer.Option(
        None,
        '--config',
        '-c',
        help='配置文件路径，默认为当前目录下的config.yaml',
    ),
) -> None:
    """运行预定义任务，可以通过任务名称或任务配置文件运行"""
    if job_name is None and job_file is None:
        console.print("[red]错误: 必须指定任务名称或任务配置文件[/red]")
        raise typer.Exit(1)

    manager = CrawlManager(config_file=config)

    if job_file is not None:
        manager.run_job_file(job_file)
    else:
        manager.run_job(job_name)


@run_app.command('spider', help='运行指定爬虫')
def run_spider(
    spider: str = typer.Argument(
        ...,
        help='爬虫名称，支持通配符，例如：stock/basic/stock_basic 或 stock/basic/*',
    ),
    config: Path = typer.Option(
        None,
        '--config',
        '-c',
        help='配置文件路径，默认为当前目录下的config.yaml',
    ),
) -> None:
    """运行指定爬虫，支持通配符匹配多个爬虫"""
    manager = CrawlManager(config_file=config)
    manager.run_spider(spider)
