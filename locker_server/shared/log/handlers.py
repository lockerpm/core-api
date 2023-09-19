import logging
import requests

from django.conf import settings


class SlackHandler(logging.Handler):
    def emit(self, record):
        try:
            record.exc_info = record.exc_text = None
            content = {'text': self.format(record)}
            # TODO authorize to thread job
            requests.post(
                url=settings.SLACK_WEBHOOK_API_LOG,
                json={"text": "```{}```".format(content['text'])},
                timeout=10
            )
        except Exception:
            print("Slack handler failed")
