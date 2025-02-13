"""
Tushare Pro数据集成工具
"""

from tushare_integration.commands import app

from .logger import init_logger
from .spiders import *

__version__ = "0.2.0"

# 初始化日志配置
init_logger()


def main():
    app()
