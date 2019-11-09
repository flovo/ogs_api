#!/usr/bin/python3

from pathlib import Path

path_incident_auth = Path('.cache/tokens/incident_auth.json')
path_chat_auth = Path('.cache/tokens/chat_auth.json')
path_notification_auth = Path('.cache/tokens/notification_auth.json')
path_user_jwt = Path('.cache/tokens/user_jwt.json')
path_data = Path('.cache/ui_config.json')


def update_tokens():
    from ogs_api.rest_api import access_api
    from json import dump as json_dump
    req = access_api('/api/v1/ui/config')
    with path_data.open("w") as fd:
        json_dump(req, fd)
    with path_chat_auth.open('w') as fd:
        json_dump(req['chat_auth'], fd)
    with path_incident_auth.open('w') as fd:
        json_dump(req['incident_auth'], fd)
    with path_notification_auth.open('w') as fd:
        json_dump(req['notification_auth'], fd)
    with path_user_jwt.open('w') as fd:
        json_dump(req['user_jwt'], fd)


def _get_auth(path):
    if not path.exists():
        update_tokens()
    from json import load as json_load
    with path.open() as fd:
        return json_load(fd)


def get_chat_auth():
    return _get_auth(path_chat_auth)


def get_incident_auth():
    return _get_auth(path_incident_auth)


def get_notification_auth():
    return _get_auth(path_notification_auth)


def get_user_jwt():
    return _get_auth(path_user_jwt)


def get_data():
    return _get_auth(path_data)

