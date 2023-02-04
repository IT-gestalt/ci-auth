import logger
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.service import Service

if __name__ == '__main__':
    Service('localhost', 9000, b'AUTH_KEY').serve_forever()
