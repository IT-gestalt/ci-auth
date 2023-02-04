from multiprocessing import Queue
from queue import Empty
import logging
import time
#
from . import abstract

TIMEOUT = 30


class Service(abstract.SuperManager):
    event_loop = Queue()

    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('put_event', callable=self.put_event)
        self.register('get_event', callable=self.get_event)

    def get_event(self, *args, **kwargs):
        try:
            event = self.event_loop.get(*args, block=False, timeout=TIMEOUT, **kwargs)
            logging.info(f"[{self.__class__.__name__}] event was get from queue: {event}.")
            logging.info(f"[{self.__class__.__name__}] events count become: {self.event_loop.qsize()}.")
            return event
        except Empty:
            logging.info(f"[{self.__class__.__name__}] have not any event in queue.")
            return None

    def put_event(self, event, *args, **kwargs):
        self.event_loop.put(event, *args, timeout=TIMEOUT, **kwargs)
        logging.info(f"[{self.__class__.__name__}] event was put to queue: {event}.")
        logging.info(f"[{self.__class__.__name__}] events count become: {self.event_loop.qsize()}.")

    def serve_forever(self):
        logging.info(f"[{self.__class__.__name__}] start listening.")
        self.dispatcher.get_server().serve_forever()
