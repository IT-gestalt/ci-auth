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
    Client(app_config.HOST, app_config.PORT, app_config.AUTH_KEY).connect().put_event(
        dict(
            datetime=datetime.datetime.now().isoformat()
        )
    )
