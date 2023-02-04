from . import event
from . import manager
from . import manager_app_config
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.client import Client
from core.base.service import Service


class UserService(Service):  # Syntactic sugar
    ...


class DynamicManagerClientInUserSide(manager.ManagerClient):  # Syntactic sugar
    ...


class UserClient(Client):
    session_token = None

    @staticmethod
    def authenticate(login, password):
        DynamicManagerClientInUserSide(manager_app_config.HOST,
                                       manager_app_config.PORT,
                                       manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="user",
                destination="authenticator",
                operation="authenticate",
                parameters=dict(
                    login=login,
                    password=password
                )
            )
        )

    def wait_for_authenticate(self):
        while True:
            # TODO: it can be personalized for each User-client
            try:
                event_obj = self.get_event()
                if event_obj is None:
                    continue
                if event_obj == event.Event(
                        source="authenticator",
                        destination="user",
                        operation="authenticate_response"):
                    return event_obj
                else:
                    self.put_event(event_obj)
            except Exception as e:
                raise e

    def check_session_token(self):
        DynamicManagerClientInUserSide(manager_app_config.HOST,
                                       manager_app_config.PORT,
                                       manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="user",
                destination="authenticator",
                operation="check_session_token",
                parameters=dict(
                    session_token=self.session_token
                )
            )
        )

    def wait_for_check_session_token(self):
        while True:
            # TODO: it can be personalized for each User-client
            try:
                event_obj = self.get_event()
                if event_obj is None:
                    continue
                if event_obj == event.Event(
                        source="authenticator",
                        destination="user",
                        operation="check_session_token_response"):
                    return event_obj
                else:
                    self.put_event(event_obj)
            except Exception as e:
                raise e

    def get_data_from_database(self):
        DynamicManagerClientInUserSide(manager_app_config.HOST,
                                       manager_app_config.PORT,
                                       manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="user",
                destination="authenticator",
                operation="get_data_from_database",
                parameters=dict(
                    session_token=self.session_token
                )
            )
        )

    def wait_for_get_data_from_database(self):
        while True:
            # TODO: it can be personalized for each User-client
            try:
                event_obj = self.get_event()
                if event_obj is None:
                    continue
                if event_obj == event.Event(
                        source="authenticator",
                        destination="user",
                        operation="get_data_from_database_response"):
                    return event_obj
                else:
                    self.put_event(event_obj)
            except Exception as e:
                raise e
