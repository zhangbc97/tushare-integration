import importlib
import os
from typing import Dict, List, Type

import typer
from rich.console import Console
from rich.table import Table

from tushare_integration.models.core import Base
from tushare_integration.manager import CrawlManager

console = Console()
api_app = typer.Typer(name='api', help='API管理', no_args_is_help=True)


def load_all_models() -> List[Type[Base]]:
    """加载所有模型类"""
    models = []
    models_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(os.path.dirname(models_dir), 'models')

    # 遍历models目录下的所有.py文件
    for filename in os.listdir(models_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            module_name = f"tushare_integration.models.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                # 获取模块中的所有类
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    # 检查是否是Base的子类，并且有API相关属性
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, Base)
                        and attr != Base
                        and hasattr(attr, '__api_name__')
                    ):
                        models.append(attr)
            except ImportError as e:
                console.print(f"[yellow]警告: 无法导入模块 {module_name}: {e}[/yellow]")

    return models


def get_api_info() -> Dict[str, Dict]:
    """获取所有API信息"""
    api_info = {}
    for model in load_all_models():
        api_name = getattr(model, '__api_name__', None)
        api_path = getattr(model, '__api_path__', [])
        # 只有当api_name存在且api_path长度为1时才添加到api_info中
        if api_name and api_name not in api_info and len(api_path) != 1:
            api_info[api_name] = {
                'title': getattr(model, '__api_title__', ''),
                'info_title': getattr(model, '__api_info_title__', ''),
                'path': api_path,
                'points_required': getattr(model, '__api_points_required__', 0),
                'special_permission': getattr(model, '__api_special_permission__', False),
                'has_vip': getattr(model, '__has_vip__', False),
                'params': getattr(model, '__api_params__', {}),
                'dependencies': getattr(model, '__dependencies__', []),
                'model': model.__name__,
            }
    return api_info


@api_app.command('list', help='列出所有可用API')
def list_apis() -> None:
    """列出所有可用的API"""
    manager = CrawlManager()
    spiders_info = manager.list_spiders()

    # 按路径排序
    spiders_info.sort(key=lambda x: x['api_path'])

    # 创建表格
    table = Table(title="API列表")

    # 添加列
    table.add_column("名称", style="bright_green")
    table.add_column("接口", style="bright_blue")
    table.add_column("中文路径", style="bright_yellow")
    table.add_column("英文路径", style="bright_magenta")
    table.add_column("所需积分", style="bright_cyan")
    table.add_column("特殊权限", style="bright_red")

    # 添加行
    for spider in spiders_info:
        # 获取spider类和model类以获取额外信息
        spider_cls = manager.process.spider_loader.load(spider['name'])
        model = getattr(spider_cls, '__model__', None)
        
        points = str(getattr(model, '__api_points_required__', '0')) if model else '0'
        special = '是' if getattr(model, '__api_special_permission__', False) else '否'

        table.add_row(
            spider['api_title'],
            spider['name'],
            spider['api_path'],
            spider['api_path_en'],
            points,
            special
        )

    # 打印表格
    console.print(table)


@api_app.command('info', help='查看特定API的详细信息')
def api_info(api_name: str = typer.Argument(..., help='API名称')) -> None:
    """查看特定API的详细信息"""
    manager = CrawlManager()
    spiders_info = manager.list_spiders(api_name)

    if not spiders_info:
        console.print(f"[red]未找到API: {api_name}[/red]")
        return

    spider_info = spiders_info[0]
    spider_cls = manager.process.spider_loader.load(spider_info['name'])
    model = getattr(spider_cls, '__model__', None)

    # 创建表格
    table = Table(title=f"API详细信息: {api_name}")

    # 添加信息行
    table.add_column("属性", style="bright_blue")
    table.add_column("值", style="bright_green")

    table.add_row("名称", spider_info['api_title'])
    table.add_row("接口", spider_info['name'])
    table.add_row("中文路径", spider_info['api_path'])
    table.add_row("英文路径", spider_info['api_path_en'])

    if model:
        table.add_row("所需积分", str(getattr(model, '__api_points_required__', '0')))
        table.add_row("特殊权限", '是' if getattr(model, '__api_special_permission__', False) else '否')
        table.add_row("VIP专享", '是' if getattr(model, '__has_vip__', False) else '否')

        # 显示API参数信息
        api_params = getattr(model, '__api_params__', {})
        if api_params:
            params_table = []
            for param_name, param_info in api_params.items():
                required = '是' if param_info.get('required', False) else '否'
                param_type = param_info.get('type', '')
                description = param_info.get('description', '')
                params_table.append(f"{param_name} ({param_type})\n  必填: {required}\n  说明: {description}")
            
            table.add_row("参数列表", "\n".join(params_table))

    # 获取依赖信息
    dependencies = manager.get_dependencies([spider_info['name']])
    if dependencies:
        table.add_row("依赖", "\n".join(dependencies))

    # 打印表格
    console.print(table)
