import importlib
import os
from typing import Dict, List, Type

import typer
from rich.console import Console
from rich.table import Table

from tushare_integration.models.core import Base

console = Console()
api_app = typer.Typer(
    name='api',
    help='API管理',
    no_args_is_help=True
)


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
                    if (isinstance(attr, type) and 
                        issubclass(attr, Base) and 
                        attr != Base and
                        hasattr(attr, '__api_name__')):
                        models.append(attr)
            except ImportError as e:
                console.print(f"[yellow]警告: 无法导入模块 {module_name}: {e}[/yellow]")
    
    return models


def get_api_info() -> Dict[str, Dict]:
    """获取所有API信息"""
    api_info = {}
    for model in load_all_models():
        api_name = getattr(model, '__api_name__', None)
        if api_name and api_name not in api_info:
            api_info[api_name] = {
                'title': getattr(model, '__api_title__', ''),
                'info_title': getattr(model, '__api_info_title__', ''),
                'path': getattr(model, '__api_path__', []),
                'points_required': getattr(model, '__api_points_required__', 0),
                'special_permission': getattr(model, '__api_special_permission__', False),
                'has_vip': getattr(model, '__has_vip__', False),
                'params': getattr(model, '__api_params__', {}),
                'dependencies': getattr(model, '__dependencies__', []),
                'model': model.__name__
            }
    return api_info


@api_app.command('list', help='列出所有可用的Tushare API')
def list_apis():
    """列���所有可用的Tushare API"""
    api_info = get_api_info()
    
    # 创建表格
    table = Table(title="Tushare API列表")
    
    # 添加列
    table.add_column("API名称", style="bright_blue")
    table.add_column("描述", style="bright_green")
    table.add_column("路径", style="bright_yellow")
    table.add_column("积分", style="bright_magenta")
    table.add_column("需单独开通", style="bright_red")
    table.add_column("含VIP接口", style="bright_cyan")
    
    # 添加行
    for api_name, info in sorted(api_info.items()):
        table.add_row(
            api_name,
            info['title'],
            ' > '.join(info['path']),
            str(info['points_required']),
            "是" if info['special_permission'] else "否",
            "是" if info['has_vip'] else "否"
        )
    
    # 打印表格
    console.print(table)


@api_app.command('info', help='查看特定API的详细信息')
def api_info(api_name: str = typer.Argument(..., help='API名称')):
    """查看特定API的详细信息"""
    api_info = get_api_info()
    
    if api_name not in api_info:
        console.print(f"[red]未找到API: {api_name}[/red]")
        return
    
    info = api_info[api_name]
    
    # 创建表格
    table = Table(title=f"API详细信息: {api_name}")
    
    # 添加信息行
    table.add_column("属性", style="bright_blue")
    table.add_column("值", style="bright_green")
    
    table.add_row("名称", info['title'])
    table.add_row("分类", info['info_title'])
    table.add_row("路径", ' > '.join(info['path']))
    table.add_row("所需积分", str(info['points_required']))
    table.add_row("需单独开通", "是" if info['special_permission'] else "否")
    table.add_row("含VIP接口", "是" if info['has_vip'] else "否")
    table.add_row("对应模型", info['model'])
    
    if info['dependencies']:
        table.add_row("依赖接口", "\n".join(info['dependencies']))
    
    if info['params']:
        param_table = Table(show_header=True, header_style="bright_blue")
        param_table.add_column("参数名")
        param_table.add_column("类型")
        param_table.add_column("必填")
        param_table.add_column("描述")
        
        for param_name, param_info in info['params'].items():
            param_table.add_row(
                param_name,
                param_info.get('type', ''),
                '是' if param_info.get('required', False) else '否',
                param_info.get('description', '')
            )
        
        table.add_row("参数列表", param_table)
    
    # 打印表格
    console.print(table) 