import typer
from rich.console import Console
from rich.table import Table

from tushare_integration.manager import CrawlManager

console = Console()
spider_app = typer.Typer(
    name='spider',
    help='爬虫管理',
    no_args_is_help=True
)


@spider_app.command('list', help='列出所有可用爬虫')
def list_spiders():
    """列出所有可用的爬虫"""
    manager = CrawlManager()
    spiders_info = manager.list_spiders()
    
    # 按路径排序
    spiders_info.sort(key=lambda x: x['api_path'])
    
    # 创建表格
    table = Table(title="爬虫列表")
    
    # 添加列
    table.add_column("名称", style="bright_green")
    table.add_column("接口", style="bright_blue")
    table.add_column("路径", style="bright_yellow")
    
    # 添加行
    for spider in spiders_info:
        table.add_row(
            spider['api_title'],
            spider['name'],
            spider['api_path']
        )
    
    # 打印表格
    console.print(table)


@spider_app.command('info', help='查看特定爬虫的详细信息')
def spider_info(spider_name: str = typer.Argument(..., help='爬虫名称')):
    """查看特定爬虫的详细信息"""
    manager = CrawlManager()
    spiders_info = manager.list_spiders(spider_name)
    
    if not spiders_info:
        console.print(f"[red]未找到爬虫: {spider_name}[/red]")
        return
    
    spider_info = spiders_info[0]
    
    # 创建表格
    table = Table(title=f"爬虫详细信息: {spider_name}")
    
    # 添加信息行
    table.add_column("属性", style="bright_blue")
    table.add_column("值", style="bright_green")
    
    table.add_row("名称", spider_info['api_title'])
    table.add_row("接口", spider_info['name'])
    table.add_row("路径", spider_info['api_path'])
    
    # 获取依赖信息
    dependencies = manager.get_dependencies([spider_name])
    if dependencies:
        table.add_row("依赖", "\n".join(dependencies))
    
    # 打印表格
    console.print(table) 