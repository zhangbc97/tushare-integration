import logging

import typer

from tushare_integration.logger import init_logger


def verbose_callback(value: bool) -> bool:
    """verbose选项的回调函数，用于设置日志级别"""
    if value:
        init_logger(logging.DEBUG)
    return value


VerboseOption = typer.Option(
    False,
    "--verbose",
    "-v",
    help="增加日志输出详细程度。使用 -v 显示DEBUG级别日志",
    callback=verbose_callback,
)


def app_callback(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="增加日志输出详细程度。使用 -v 显示DEBUG级别日志",
        callback=verbose_callback,
    ),
): ...
