import importlib
import logging

import requests

from tushare_integration.settings import TushareIntegrationSettings


class Reporter(object):
    def __init__(self, settings: TushareIntegrationSettings) -> None:
        self.settings = settings

    def send_report(self, subject: str, content: str, *args, **kwargs):
        raise NotImplementedError


class FeishuWebHookReporter(Reporter):

    def __init__(self, settings: TushareIntegrationSettings) -> None:
        self.settings = settings
        self.webhook = self.settings.feishu_webhook

    def send_report(self, subject: str, content: str, *args, **kwargs):
        if not self.webhook:
            logging.info('No feishu webhook, skip send report')
            return

        content = f'**{subject}**\n{content}'

        body = {"msg_type": "text", "content": {"text": content}}

        resp = requests.post(self.webhook, json=body)
        logging.info(f'Send report to feishu webhook, status code: {resp.status_code}, response: {resp.text}')


class ReporterLoader(object):
    def __init__(self, settings: TushareIntegrationSettings):
        self.settings = settings
        self.reporters = settings.reporters
        logging.info(f'Load reporters: {self.reporters}')

    def get_reporters(self) -> list[Reporter]:
        reporters = []
        for reporter in self.reporters:
            package, class_name = reporter.rsplit('.', 1)
            module = importlib.import_module(package)
            cls = getattr(module, class_name)
            reporters.append(cls(self.settings))

        return reporters
