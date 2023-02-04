from logger import logging
import logger

from model.manager import ManagerService
from model import manager_app_config as config


if __name__ == '__main__':
    ManagerService(config.HOST,
                   config.PORT,
                   config.SECRET_KEY).serve_forever()
