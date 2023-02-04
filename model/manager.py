import logging
import time
#
from . import authenticator_app_config
from . import manager_policy
from . import user_app_config
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.client import Client
from core.base.service import Service

ENTITIES_SERVICES = dict(
    authenticator=dict(
        HOST=authenticator_app_config.HOST,
        PORT=authenticator_app_config.PORT,
        SECRET_KEY=authenticator_app_config.SECRET_KEY
    ),
    user=dict(
        HOST=user_app_config.HOST,
        PORT=user_app_config.PORT,
        SECRET_KEY=user_app_config.SECRET_KEY
    )
)


class ManagerService(Service):

    def put_event(self, event_obj, *args, **kwargs):
        if manager_policy.check_by_policy(event_obj):
            logging.info(f"[{self.__class__.__name__}] check by policy event {event_obj}.")
            super().put_event(event_obj, *args, **kwargs)
        else:
            logging.warning(f"[{self.__class__.__name__}] ignore not policy event {event_obj}.")


class DelegatorToAnotherEntityClient(Client):  # Syntactic sugar
    ...


class ManagerClient(Client):

    def process_event_loop(self):
        while True:
            try:
                event_obj = self.get_event()
                if event_obj is None:
                    continue
                logging.info(f"[{self.__class__.__name__}] delegate {event_obj.destination} to event {event_obj}.")
                connection_config = ENTITIES_SERVICES.get(event_obj.destination)
                delegate_to_destination = DelegatorToAnotherEntityClient(connection_config.get("HOST"),
                                                                         connection_config.get("PORT"),
                                                                         connection_config.get("SECRET_KEY")).connect()
                delegate_to_destination.put_event(event_obj)

                # TODO: if error on delegate manager must response Error to initiator
                # TODO: may be it will be good to put back the braked-Event with incremental counter
            except ConnectionRefusedError as e:
                logging.warning(f"[{self.__class__.__name__}] ConnectionRefusedError {e}.")
                continue
            except Exception as e:
                logging.error(f"[{self.__class__.__name__}] Exception {e}.")
                raise e
