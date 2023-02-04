import logger

from model.authenticator import AuthenticatorClient
from model import authenticator_app_config as config

if __name__ == '__main__':
    AuthenticatorClient(config.HOST,
                        config.PORT,
                        config.SECRET_KEY).connect().process_event_loop()
