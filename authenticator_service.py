import logger

from model.authenticator import AuthenticatorService
from model import authenticator_app_config as config

if __name__ == '__main__':
    AuthenticatorService(config.HOST,
                         config.PORT,
                         config.SECRET_KEY).serve_forever()
