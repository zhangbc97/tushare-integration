import re
import signal
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from sqlalchemy import select

from tushare_integration.crawler.pipeline import TushareIntegrationLog
from tushare_integration.crawler.spider import Spider, SpiderMeta
from tushare_integration.db_engine import DBEngine
from tushare_integration.dictionary import API_PATH_DICTIONARY
from tushare_integration.reporters import ReporterLoader
from tushare_integration.settings import TushareIntegrationSettings, load_config

console = Console()


class TushareIntegrationManager(object):
    """TushareIntegration管理器"""

    def __init__(self) -> None: ...

    def list_spiders(self, pattern: Optional[str] = None) -> List[Dict[str, str]]: ...

    def list_apis(self, pattern: Optional[str] = None) -> List[Dict[str, str]]: ...


class CrawlManager(object):
    """爬虫管理器"""

    def __init__(self, config_file: Optional[Path] = None) -> None:
        """初始化爬虫管理器

        Args:
            config_file: 配置文件路径，默认为当前目录下的config.yaml
        """
        if config_file is None:
            config_file = Path('config.yaml')

        # 检查配置文件
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_file}")

        # 加载配置
        self.config_file = config_file
        self.batch_id = uuid.uuid1().hex
        self.settings: TushareIntegrationSettings = load_config(config_file)
        self.db_engine: DBEngine = DBEngine(self.settings)
        self.reporter_loader: ReporterLoader = ReporterLoader(self.settings)

        # 注册系统信号处理器
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def list_spiders(self, pattern: Optional[str] = None) -> List[Dict[str, str]]:
        """列出所有爬虫

        Args:
            pattern: 爬虫名称匹配模式

        Returns:
            爬虫信息列表，每个元素包含api_title、name、api_path和api_path_en
        """
        # SpiderMeta.get_all_spiders()获取所有爬虫类
        spiders = SpiderMeta.get_all_spiders()

        # 过滤
        if pattern:
            spiders = {name: spider_cls for name, spider_cls in spiders.items() if re.fullmatch(pattern, name)}

        # 创建中文到英文的映射字典
        cn_to_en_dict = {k: v for k, v in API_PATH_DICTIONARY.items()}

        spider_info_list = []
        for spider_name, spider_cls in spiders.items():
            # 获取model类
            model = getattr(spider_cls, '__model__', None)
            if model:
                api_path = getattr(model, '__api_path__', [])
                # 转换为英文路径，跳过第一个元素
                api_path_en = []
                for i, path in enumerate(api_path[1:], 1):  # 从第二个元素开始，保持索引正确
                    if i == len(api_path) - 1:
                        # 最后一级使用__api_name__
                        api_path_en.append(getattr(model, '__api_name__', path))
                    else:
                        en_path = cn_to_en_dict.get(path, path)
                        api_path_en.append(en_path)

                spider_info_list.append(
                    {
                        'api_title': getattr(model, '__api_title__', ''),
                        'name': spider_name,
                        'api_path': ' > '.join(api_path),
                        'api_path_en': '/'.join(api_path_en),
                    }
                )

        return spider_info_list

    def run_spider(self, pattern: str) -> None: ...

    def run_job(self, job_name: str) -> None: ...

    def get_settings(self) -> Dict[str, Any]:
        """获爬虫设置"""
        settings = self.settings.get_settings()
        settings['LOG_LEVEL'] = 'INFO'
        settings['BATCH_ID'] = self.batch_id
        return settings

    def send_report(self) -> None:
        """发送报告"""
        for reporter in self.reporter_loader.get_reporters():
            reporter.send_report(subject='数据更新通知', content=self.get_report_content())

    def get_report_content(self) -> str:
        """获取报告内容"""
        with self.db_engine.session() as session:
            logs = (
                session.execute(select(TushareIntegrationLog).where(TushareIntegrationLog.batch_id == self.batch_id))
                .scalars()
                .all()
            )

            content = f"Batch ID: {self.batch_id}\n\n"

            # 添加爬虫运行状态
            for log in logs:
                content += f"Spider: {log.spider_name} Count: {log.count}\n"

            # TODO 添TODO加警告信息

            return content

    def stop(self, signum: int, frame: Any) -> None:
        """停止爬虫"""
        console.print("[yellow]Received stop signal, stopping...[/yellow]")
        self.send_report()

    def _list_spiders_by_path(self, path_pattern: str) -> List[Dict[str, str]]:
        """内部方法：通过API路径模式匹配爬虫

        Args:
            path_pattern: API路径匹配模式，如 'stock/basic'

        Returns:
            匹配的爬虫列表
        """
        path_parts = path_pattern.strip('/').split('/')
        cn_path_parts = []

        # 创建反向映射字典
        reverse_dict = {v: k for k, v in API_PATH_DICTIONARY.items()}

        for part in path_parts:
            if part in reverse_dict:
                cn_path_parts.append(reverse_dict[part])
            else:
                cn_path_parts.append(part)

        spider_names = self.process.spider_loader.list()
        spider_info_list = []

        for spider_name in spider_names:
            spider_cls = self.process.spider_loader.load(spider_name)
            model = getattr(spider_cls, '__model__', None)

            if model and hasattr(model, '__api_path__'):
                api_path = model.__api_path__

                # 跳过第一个元素进行匹配
                match = True
                for i, pattern in enumerate(cn_path_parts):
                    # 直接从第二个元素开始匹配
                    api_path_index = i + 1
                    if api_path_index >= len(api_path):
                        match = False
                        break
                    if not re.fullmatch(pattern, api_path[api_path_index]):
                        match = False
                        break

                if match:
                    # 转换为英文路径，跳过第一个元素
                    api_path_en = []
                    for i, path in enumerate(api_path[1:], 1):  # 从第二个元素开始，保持索引正确
                        if i == len(api_path) - 1:
                            # 最后一级使用__api_name__
                            api_path_en.append(getattr(model, '__api_name__', path))
                        else:
                            en_path = reverse_dict.get(path, path)
                            api_path_en.append(en_path)

                    spider_info_list.append(
                        {
                            'api_title': getattr(model, '__api_title__', ''),
                            'name': spider_name,
                            'api_path': ' > '.join(api_path),
                            'api_path_en': '/'.join(api_path_en),
                        }
                    )

        return spider_info_list
