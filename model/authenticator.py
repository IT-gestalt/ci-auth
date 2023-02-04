import uuid
import logging
#
from . import event
from . import manager_app_config
from . import manager
#
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.base.client import Client
from core.base.service import Service


# TODO: must be foreign entity
class Database:
    accounts = dict()  # (login, password) = session_token
    accounts[("user", "user")] = None
    accounts[("admin", "admin")] = None
    accounts[("root", "root")] = None

    data = list()  # Demonstration database data
    data.append(dict(value="One"))
    data.append(dict(value="Two", message=":)"))
    data.append(dict(value="Three"))

    @classmethod
    def _is_account_exists(cls, login, password):
        if (login, password) in Database.accounts:
            return True
        return False

    @classmethod
    def authenticate(cls, login, password):
        if Database._is_account_exists(login, password):
            session_token = str(uuid.uuid4())
            Database.accounts[(login, password)] = session_token
            return session_token
        return None

    @classmethod
    def is_account_authenticate(cls, session_token):
        if session_token is not None and session_token in Database.accounts.values():
            return True
        return False

    @classmethod
    def get_data_from_database(cls):
        return Database.data


class AuthenticatorService(Service):  # Syntactic sugar
    ...


class DynamicManagerClientInAuthenticatorSide(manager.ManagerClient):  # Syntactic sugar
    ...


class AuthenticatorClient(Client):

    def process_event_loop(self):
        while True:
            event_obj = self.get_event()
            if event_obj is None:
                continue
            # TODO: need check Event-signature by event.operation
            operation = event_obj.operation
            if operation == "authenticate":
                login = event_obj.parameters.get("login", "")
                password = event_obj.parameters.get("password", "")
                if login and password:
                    AuthenticatorClient.authenticate(login, password)
            elif operation == "check_session_token":
                session_token = event_obj.parameters.get("session_token", "")
                AuthenticatorClient.check_session_token(session_token)
            elif operation == "get_data_from_database":
                session_token = event_obj.parameters.get("session_token", "")
                AuthenticatorClient.get_data_from_database(session_token)

    @staticmethod
    def authenticate(login, password):
        session_token = Database.authenticate(login, password)
        if session_token is None:
            DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                    manager_app_config.PORT,
                                                    manager_app_config.SECRET_KEY) \
                .connect() \
                .put_event(
                event.Event(
                    source="authenticator",
                    destination="user",
                    operation="authenticate_response",
                    parameters=dict(
                        status="error",
                        message="authentication was deny"
                    )
                )
            )
            return False

        DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                manager_app_config.PORT,
                                                manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="authenticator",
                destination="user",
                operation="authenticate_response",
                parameters=dict(
                    status="ok",
                    message="authentication is allow",
                    session_token=session_token,
                )
            )
        )
        return True

    @staticmethod
    def check_session_token(session_token):
        if not Database.is_account_authenticate(session_token):
            DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                    manager_app_config.PORT,
                                                    manager_app_config.SECRET_KEY) \
                .connect() \
                .put_event(
                event.Event(
                    source="authenticator",
                    destination="user",
                    operation="check_session_token_response",
                    parameters=dict(
                        status="error",
                        message="session token is invalid"
                    )
                )
            )
            return False

        DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                manager_app_config.PORT,
                                                manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="authenticator",
                destination="user",
                operation="check_session_token_response",
                parameters=dict(
                    status="ok",
                    message="session token is valid"
                )
            )
        )
        return True

    @staticmethod
    def get_data_from_database(session_token):
        if not Database.is_account_authenticate(session_token):
            DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                    manager_app_config.PORT,
                                                    manager_app_config.SECRET_KEY) \
                .connect() \
                .put_event(
                event.Event(
                    source="authenticator",
                    destination="user",
                    operation="get_data_from_database_response",
                    parameters=dict(
                        status="error",
                        message="session token is invalid"
                    )
                )
            )
            return False

        DynamicManagerClientInAuthenticatorSide(manager_app_config.HOST,
                                                manager_app_config.PORT,
                                                manager_app_config.SECRET_KEY) \
            .connect() \
            .put_event(
            event.Event(
                source="authenticator",
                destination="user",
                operation="get_data_from_database_response",
                parameters=dict(
                    status="ok",
                    data=Database.get_data_from_database()
                )
            )
        )
        return True
