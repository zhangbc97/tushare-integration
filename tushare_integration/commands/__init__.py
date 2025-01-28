import typer

from tushare_integration.commands.base import app_callback

# 导入子命令
from .api import api_app
from .config import config_app
from .run import run_app
from .spider import spider_app

# 创建主命令app，设置rich_help_panel来分组全局选项
app = typer.Typer(
    name='tushare',
    help='Tushare数据集成工具',
    no_args_is_help=True,
    rich_help_panel="全局选项",
    callback=app_callback,
)


# 注册子命令
app.add_typer(run_app, name='run')
app.add_typer(spider_app, name='spider')
app.add_typer(api_app, name='api')
app.add_typer(config_app, name='config')
