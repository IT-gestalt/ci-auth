import logger

from model.user import UserService
from model import user_app_config as config

if __name__ == '__main__':
    UserService(config.HOST,
                config.PORT,
                config.SECRET_KEY).serve_forever()
