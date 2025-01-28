from pathlib import Path

import typer
from rich.console import Console

from tushare_integration.manager import TushareIntegrationManager

console = Console()
run_app = typer.Typer(name='run', help='运行爬虫或任务', no_args_is_help=True)


@run_app.command('job', help='运行预定义任务')
def run_job(
    job_file: Path = typer.Argument(
        ...,
        help='任务配置文件路径，例如：jobs.yaml',
    ),
    job_name: str = typer.Option(
        None,
        '--job',
        '-j',
        help='可选的任务名称，如果指定则只运行该任务',
    ),
    config: Path = typer.Option(
        None,
        '--config',
        '-c',
        help='配置文件路径，默认为当前目录下的config.yaml',
    ),
) -> None:
    """运行预定义任务，需要指定任务配置文件路径，可选指定具体任务名称"""
    manager = TushareIntegrationManager(config_file=config)
    manager.run_job(job_file=job_file.as_posix(), job_name=job_name)


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
    manager = TushareIntegrationManager(config_file=config)
    manager.run_spider(spider)
