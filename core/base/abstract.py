import logging
from multiprocessing.managers import (
    BaseManager,
)


class SuperManager:
    dispatcher = None

    def __init__(self, host, port, authkey):
        logging.info(f"[{self.__class__.__name__}] will be work with {host}:{port}.")
        self.dispatcher = BaseManager(address=(host, port), authkey=authkey)

    def register(self, *args, **kwargs):
        self.dispatcher.register(*args, **kwargs)
