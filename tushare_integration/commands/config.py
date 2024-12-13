from pathlib import Path
from typing import Annotated, Dict, Optional

import typer
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

console = Console()
config_app = typer.Typer(name='config', help='配置管理', no_args_is_help=True)


def get_db_template_params(db_type: str) -> Dict:
    """获取数据库模板参数"""
    if db_type == 'clickhouse':
        return {
            'engine': 'MergeTree()',
            'partition_by': 'toYYYYMM(trade_date)',
            'order_by': '(trade_date, ts_code)',
        }
    elif db_type == 'mysql':
        return {}
    elif db_type == 'doris':
        return {
            'engine': 'OLAP',
            'aggregate_key': 'trade_date, ts_code',
        }
    elif db_type == 'starrocks':
        return {
            'engine': 'OLAP',
            'duplicate_key': 'trade_date, ts_code',
        }
    return {}


def generate_jobs_config() -> str:
    """生成默认的任务配置"""
    return """# 定时任务配置
jobs:
  # 每日更新任务
  - name: daily_update  # 任务名称
    cron_expr: "0 17 * * 1-5"  # cron表���式，每个交易日下午5点执行
    spiders:  # 需要执行的爬虫列表
      - name: stock/basic/trade_cal  # 交易日历
      - name: stock/quotes/daily  # 日线行情
      - name: stock/quotes/daily_basic  # 每日指标

  # 每周更新任务
  - name: weekly_update
    cron_expr: "0 18 * * 5"  # 每周五下午6点执行
    spiders:
      - name: stock/basic/stock_basic  # 股票列表
      - name: stock/basic/stock_company  # 上市公司本信息"""


@config_app.command('init', help='交互式初始化配置')
def init_config() -> None:
    """交互式初始化配置文件"""
    # 直接使用当前目录
    config_dir = Path('.')

    # 创建配置目录
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        console.print(f"[green]创建配置目录: {config_dir}[/green]")

    # 获取Tushare配置
    console.print("\n[bold]Tushare配置[/bold]")
    tushare_token = Prompt.ask("请输入Tushare token")
    tushare_point = IntPrompt.ask("请输入Tushare积分（用于控制并发）", default=2000)
    tushare_url = Prompt.ask("请输入Tushare API地址", default="https://api.tushare.pro")

    # 获取数据库配置
    console.print("\n[bold]数据库配置[/bold]")
    db_types = ['clickhouse', 'mysql', 'doris', 'starrocks']
    for i, db_type in enumerate(db_types, 1):
        console.print(f"{i}. {db_type}")

    db_choice = IntPrompt.ask("请选择数据库类型", choices=[str(i) for i in range(1, len(db_types) + 1)])
    db_type = db_types[db_choice - 1]

    db_host = Prompt.ask("数据库主机地址", default="127.0.0.1")
    db_port = Prompt.ask("数据库端口", default="8123" if db_type == 'clickhouse' else "3306")
    db_user = Prompt.ask("数据库用户名", default="default" if db_type == 'clickhouse' else "root")
    db_password = Prompt.ask("数据库密码", password=True)
    db_name = Prompt.ask("数据库名", default="default")

    # 获取数据库模板参数
    template_params = get_db_template_params(db_type)
    if Confirm.ask("是否需要自定义数据库模板参数?"):
        console.print("\n当前模板参数：")
        for key, value in template_params.items():
            console.print(f"{key}: {value}")
        console.print("\n可以手动编辑配置文件修改这些参数")

    # 配置报告器
    reporters = []
    if Confirm.ask("\n是否启用飞书通知?"):
        webhook_url = Prompt.ask("请输入飞书 Webhook URL")
        reporters.append({'name': 'tushare_integration.reporters.FeishuWebHookReporter', 'webhook_url': webhook_url})

    # 生成配置文件
    config_content = f"""# TUSHARE相关配置
tushare_url: {tushare_url}
tushare_point: {tushare_point}
tushare_token: '{tushare_token}'

database:
  # 数据库配置
  db_type: '{db_type}'
  host: '{db_host}'
  port: '{db_port}'
  user: '{db_user}'
  password: '{db_password}'
  db_name: '{db_name}'
  template_params: {template_params}

# 报告器配置
reporters:"""

    if reporters:
        for reporter in reporters:
            config_content += f"""
  - name: "{reporter['name']}"
    webhook_url: "{reporter['webhook_url']}" """
    else:
        config_content += " []"
        config_content += """
# 例：飞书通知
#  - name: "tushare_integration.reporters.FeishuWebHookReporter"
#    webhook_url: "your_webhook_url" """

    # 写入配置文件
    config_file = config_dir / 'config.yaml'
    if config_file.exists() and not Confirm.ask(f"配置文件 {config_file} 已存在，是否覆盖?"):
        console.print("[yellow]配置初始化已取消[/yellow]")
        return

    config_file.write_text(config_content)
    console.print(f"[green]配置文件已保存到: {config_file}[/green]")

    # 创建任务配置
    jobs_file = config_dir / 'jobs.yaml'
    if not jobs_file.exists() and Confirm.ask("是否创建任务配置文件?"):
        jobs_file.write_text(generate_jobs_config())
        console.print(f"[green]任务配置文件已创建: {jobs_file}[/green]")

    console.print("\n[bold green]配置初始化完成！[/bold green]")
    console.print(f"\n配置文件位置：")
    console.print(f"1. {config_file} - Tushare和数据库配置")
    console.print(f"2. {jobs_file} - 定时任务配置（可选）")

