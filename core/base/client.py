import logging
import time

from . import abstract

SLEEP_SEC = 30  # just for demonstration


class Client(abstract.SuperManager):
    def __init__(self, host, port, authkey):
        super().__init__(host, port, authkey)
        self.register('put_event', self.put_event)
        self.register('get_event', self.get_event)

    def get_event(self, *args, **kwargs):
        logging.info(f"[{self.__class__.__name__}] send request for event get from service.")
        event_proxy_object = self.dispatcher.get_event(*args, **kwargs)
        # TODO: must better to use AutoProxy-object with some self.dispatcher.register('Event', Event, proxytype=EProxy)
        event = event_proxy_object._getvalue()
        if event is not None:
            logging.info(f"[{self.__class__.__name__}] get event {event} from service.")
        else:
            logging.info(f"[{self.__class__.__name__}] get no event response from service. Sleep {SLEEP_SEC} seconds.")
            time.sleep(SLEEP_SEC)
        return event

    def put_event(self, event, *args, **kwargs):
        logging.info(f"[{self.__class__.__name__}] put event {event}.")
        self.dispatcher.put_event(event, *args, **kwargs)

    def connect(self, *args, **kwargs):
        self.dispatcher.connect()
        logging.info(f"[{self.__class__.__name__}] connect.")
        return self
