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

if __name__ == '__main__':
    client_1 = Client(app_config.HOST, app_config.PORT, app_config.AUTH_KEY)
    client_1.connect()
    client_1.put_event(
        dict(datetime=datetime.datetime.now().isoformat())
    )

    client_2 = Client(app_config.HOST, app_config.PORT, app_config.AUTH_KEY).connect()
    client_2.put_event(
        dict(datetime=datetime.datetime.now().isoformat())
    )

    event = Client(app_config.HOST, app_config.PORT, app_config.AUTH_KEY).connect().get_event()
