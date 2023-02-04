import logger

from model.user import UserClient
from model import user_app_config as config

if __name__ == '__main__':
    user = UserClient(config.HOST,
                      config.PORT,
                      config.SECRET_KEY).connect()

    # UserClient normal strategy
    user.authenticate("user", "user")  # authentication request by login and password
    event = user.wait_for_authenticate()  # wait for authentication response
    if event.parameters.get("status") == "ok":
        user.session_token = event.parameters.get("session_token")  # get `session_token` from authentication response
        # login and password no need below for UserClient
        user.get_data_from_database()  # request of data for authenticated UserClient
        _ = user.wait_for_get_data_from_database()  # wait for data response

    # UserClient attack
    user.session_token = '0123-4567-89AB-CDEF'  # UserClient setup invalid `session_token`
    user.check_session_token()  # request of `session_token` check
    event = user.wait_for_check_session_token()  # wait for check response
    user.get_data_from_database()  # request of data for UserClient with invalid `session_token`
    _ = user.wait_for_get_data_from_database()  # wait for data response
    #
