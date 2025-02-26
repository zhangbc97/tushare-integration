from typing import Dict, List, Optional, Type

import typer
import yaml
from rich.console import Console
from rich.table import Table

from tushare_integration.commands.base import VerboseOption, app_callback
from tushare_integration.crawler.spider import Spider, SpiderMeta
from tushare_integration.dictionary import API_PATH_DICTIONARY

console = Console()
spider_app = typer.Typer(
    name='spider',
    help='爬虫管理',
    no_args_is_help=True,
    callback=app_callback,
)


def _convert_spider_to_info(spider_cls: Type[Spider]) -> Dict[str, str]:
    """将爬虫类转换为信息字典

    Args:
        spider_cls: 爬虫类

    Returns:
        包含爬虫信息的字典，包括api_title、name、api_path和api_path_en
    """
    model = spider_cls.__model__
    api_path = getattr(model, '__api_path__', [])

    # 转换为英文路径，跳过第一个元素
    api_path_en = []
    for p in api_path[1:-1]:  # 除了第一个和最后一个元素外的所有元素
        en_path = API_PATH_DICTIONARY.get(p, p)
        api_path_en.append(en_path)

    # 添加最后一个元素，使用__api_name__
    if len(api_path) > 1:
        api_path_en.append(getattr(model, '__api_name__', api_path[-1]))

    return {
        'api_title': getattr(model, '__api_title__', ''),
        'name': spider_cls.__model__.__api_name__,
        'api_path': ' > '.join(api_path),
        'api_path_en': '/'.join(api_path_en),
    }


def list_spiders_info(pattern: Optional[str] = None) -> List[Dict[str, str]]:
    """获取爬虫信息列表

    Args:
        pattern: 可选的匹配模式，支持两种格式：
            1. 爬虫名称匹配模式，如 "stock_basic"
            2. API路径匹配模式，如 "stock/basic"

    Returns:
        爬虫信息列表，每个元素包含api_title、name、api_path和api_path_en
    """
    # 根据pattern格式选择不同的查找方式
    spiders = SpiderMeta.list_spiders(pattern)
    spiders_info = [_convert_spider_to_info(spider_cls) for spider_cls in spiders]
    spiders_info.sort(key=lambda x: x['api_path'])
    return spiders_info


@spider_app.command('list', help='列出所有可用爬虫')
def cmd_list_spiders(
    verbose: bool = VerboseOption,
    pattern: Optional[str] = None,
    no_table: Optional[bool] = False,
) -> None:
    """列出所有可用的爬虫

    Args:
        pattern: 可选的匹配模式，支持两种格式：
            1. 爬虫名称匹配模式，如 "stock_basic"
            2. API路径匹配模式，如 "stock/basic"
    """
    spiders_info = list_spiders_info(pattern)

    if no_table:
        # 将spider按照api_path_en的分组，将最后一个/之前的路径作为分组的key
        spider_group = {}
        for spider in spiders_info:
            api_path_en = spider['api_path_en']
            key = '/'.join(api_path_en.split('/')[:-1])
            if key not in spider_group:
                spider_group[key] = []
            spider_group[key].append(spider['api_path_en'])

        # [
        #     {'group':'group_name','spiders':['api_path_en']}
        # ]
        spider_group_list = []
        for key, value in spider_group.items():
            spider_group_list.append({'group': key, 'spiders': value})

        console.print(yaml.dump(spider_group_list))

        return

    # 创建表格
    table = Table(title="爬虫列表")

    # 添加列
    table.add_column("名称", style="bright_green")
    table.add_column("接口", style="bright_blue")
    table.add_column("中文路径", style="bright_yellow")
    table.add_column("英文路径", style="bright_magenta")

    # 添加行
    for spider in spiders_info:
        table.add_row(spider['api_title'], spider['name'], spider['api_path'], spider['api_path_en'])

    # 打印表格
    console.print(table)


@spider_app.command('info', help='查看特定爬虫的详细信息')
def spider_info(verbose: bool = VerboseOption, spider_name: str = typer.Argument(..., help='爬虫名称或路径')) -> None:
    """查看特定爬虫的详细信息

    Args:
        spider_name: 爬虫名称或路径，支持两种格式：
            1. 爬虫名称，如 "stock_basic"
            2. API路径，如 "stock/basic"
    """
    spiders_info = list_spiders_info(spider_name)

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
    table.add_row("中文路径", spider_info['api_path'])
    table.add_row("英文路径", spider_info['api_path_en'])

    # 获取依赖信息
    dependencies = SpiderMeta.get(spider_name).__model__.__dependencies__
    if dependencies:
        table.add_row("依赖", "\n".join(dependencies))

    # 打印表格
    console.print(table)
