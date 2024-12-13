import importlib
import logging

import requests

from tushare_integration.settings import TushareIntegrationSettings


class Reporter(object):
    def send_report(self, subject: str, content: str, *args, **kwargs):
        raise NotImplementedError


class FeishuWebHookReporter(Reporter):
    def __init__(self, webhook: str, *args, **kwargs):
        self.webhook = webhook
        super(FeishuWebHookReporter, self).__init__(*args, **kwargs)

    def send_report(self, subject: str, content: str, *args, **kwargs):
        if not self.webhook:
            logging.info('No feishu webhook, skip send report')
            return

            # 将content按照\n分割
        body = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": subject,
                        "content": [[{"text": f'{_}\n', "tag": "text"} for _ in content.split('\n')]],
                    }
                }
            },
        }

        # 找到最后一个content，移除掉末尾的\n
        if body['content']['post']['zh_cn']['content'][-1][-1]['text'] == '\n':
            body['content']['post']['zh_cn']['content'][-1][-1]['text'] = body['content']['post']['zh_cn']['content'][
                -1
            ][-1]['text'][:-1]

        resp = requests.post(self.webhook, json=body)
        logging.info(f'Send report to feishu webhook, status code: {resp.status_code}, response: {resp.text}')

    @classmethod
    def from_settings(cls, settings):
        return cls(webhook=settings.get('FEISHU_WEBHOOK'))


class ReporterLoader(object):
    def __init__(self, settings: TushareIntegrationSettings):
        self.settings = settings
        self.reporters = settings.reporters
        logging.info(f'Load reporters: {self.reporters}')

    def get_reporters(self):
        reporters = []
        for reporter in self.reporters:
            package, class_name = reporter.rsplit('.', 1)
            module = importlib.import_module(package)
            cls = getattr(module, class_name)
            reporters.append(cls.from_settings(self.settings))

        return reporters
