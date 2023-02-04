import logger
import datetime
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.client import Client

if __name__ == '__main__':
    client_1 = Client('localhost', 9000, b'AUTH_KEY')
    client_1.connect()
    client_1.put_event(
        dict(datetime=datetime.datetime.now().isoformat())
    )

    client_2 = Client('localhost', 9000, b'AUTH_KEY').connect()
    client_2.put_event(
        dict(datetime=datetime.datetime.now().isoformat())
    )

    event = Client('localhost', 9000, b'AUTH_KEY').connect().get_event()
