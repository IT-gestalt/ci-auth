import logger

from model.manager import ManagerClient
from model import manager_app_config as config

if __name__ == '__main__':
    ManagerClient(config.HOST,
                  config.PORT,
                  config.SECRET_KEY).connect().process_event_loop()
