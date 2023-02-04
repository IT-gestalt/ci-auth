import logging
#
import logger
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.service import Service
import example_001_0_app_config as app_config


class Example001Service(Service):

    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('get_back_event', callable=self.get_back_event)

    def get_back_event(self, event):
        logging.info(f'[Example001Service] event was get back {event}')
        self.put_event(event)


if __name__ == '__main__':
    Example001Service(app_config.HOST, app_config.PORT, app_config.AUTH_KEY).serve_forever()
