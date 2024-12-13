import typer

app = typer.Typer(
    name='tushare',
    help='Tushare数据集成工具',
    no_args_is_help=True
)

# 导入子命令
from .run import run_app
from .spider import spider_app
from .api import api_app

# 注册子命令
app.add_typer(run_app, name='run')
app.add_typer(spider_app, name='spider')
app.add_typer(api_app, name='api') 