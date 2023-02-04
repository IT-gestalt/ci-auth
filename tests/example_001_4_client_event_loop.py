import time
import logging
import datetime
#
import logger
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.client import Client
import example_001_0_app_config as app_config


class Example001Client(Client):
    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('get_back_event', self.get_back_event)

    def get_back_event(self, event):
        logging.info(f'[Example001Client] get back event {event}')
        self.dispatcher.get_back_event(event)


if __name__ == '__main__':
    client = Example001Client(app_config.HOST, app_config.PORT, app_config.AUTH_KEY).connect()
    client.put_event(
        dict(
            datetime=datetime.datetime.now().isoformat()
        )
    )
    while True:
        time.sleep(2)
        event = client.get_event()
        if event is None:
            continue
        client.get_back_event(event)
