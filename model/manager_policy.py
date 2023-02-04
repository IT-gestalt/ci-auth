from . import event

SECURITY_POLICY = event.Event(source="user", destination="authenticator", operation="authenticate"), \
                  event.Event(source="authenticator", destination="user", operation="authenticate_response"), \
                  event.Event(source="user", destination="authenticator", operation="check_session_token"), \
                  event.Event(source="authenticator", destination="user", operation="check_session_token_response"), \
                  event.Event(source="user", destination="authenticator", operation="get_data_from_database"), \
                  event.Event(source="authenticator", destination="user", operation="get_data_from_database_response")


def check_by_policy(_event):
    if _event in SECURITY_POLICY:
        return True
    return False
