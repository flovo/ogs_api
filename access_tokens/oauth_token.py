import json
from pathlib import Path
from ogs_utils.input import ask_for_input
from time import time
import requests
import os
from time import sleep
from threading import Lock

_oauth_token = None
_expires = time() - 1

lock = Lock()


def get_oauth_token(username=None,
                    password=None,
                    client_id=None,
                    client_secret=None,
                    settings_file=".settings/oauth_credentials.json",
                    oauth_token_file=".cache/tokens/oauth_token.json",
                    beta=False):
    global _expires
    global _oauth_token
    global lock
    with lock:
        if _expires > time():
            return _oauth_token
        settings_path = Path(settings_file + (".beta" if beta else ""))
        if settings_path.exists():
            with settings_path.open() as fd:
                cred = json.load(fd)
            if username is None:
                username = cred.get('username', None)
            if password is None:
                password = cred.get('password', None)
            if client_id is None:
                client_id = cred.get('client_id', None)
            if client_secret is None:
                client_secret = cred.get('client_secret', None)
        oauth_path = Path(oauth_token_file + (".beta" if beta else ""))
        if oauth_path.exists():
            with oauth_path.open() as fd:
                token = json.load(fd)
            if time() < token['expires']:
                _oauth_token = {'Authorization': 'Bearer {}'.format(token['access_token'])}
                _expires = token['expires']
                return _oauth_token
            print("requesting new token using old token")
            if username is None:
                username = ask_for_input('username')
            if client_id is None:
                client_id = ask_for_input('client_id')
            if client_secret is None:
                client_secret = ask_for_input('client_secret')
            if beta:
                req = requests.post('https://beta.online-go.com/oauth2/token/',
                                    data={'username': username,
                                          'refresh_token': token['refresh_token'],
                                          'client_id': client_id,
                                          'client_secret': client_secret,
                                          'grant_type': 'refresh_token'})
            else:
                req = requests.post('https://online-go.com/oauth2/token/',
                                    data={'username': username,
                                          'refresh_token': token['refresh_token'],
                                          'client_id': client_id,
                                          'client_secret': client_secret,
                                          'grant_type': 'refresh_token'})
            try:
                new_token = req.json()
            except json.JSONDecodeError:
                sleep(1)
                return get_oauth_token(username=username,
                        password=password,
                        client_id=client_id,
                        client_secret=client_secret,
                        settings_file=settings_file,
                        oauth_token_file=oauth_token_file,
                        beta=beta)
        else:
            print("requesting completely new token")
            if username is None:
                username = ask_for_input('username')
            if password is None:
                password = ask_for_input('password')
            if client_id is None:
                client_id = ask_for_input('client_id')
            if client_secret is None:
                client_secret = ask_for_input('client_secret')
            req = requests.post('https://online-go.com/oauth2/token/',
                                data={'username': username,
                                      'password': password,
                                      'client_id': client_id,
                                      'client_secret': client_secret,
                                      'grant_type': 'password'})
            new_token = req.json()
        try:
            token = {'access_token': new_token['access_token'],
                     'token_type': new_token['token_type'],
                     'refresh_token': new_token['refresh_token'],
                     'scope': new_token['scope'],
                     'expires': time() + new_token['expires_in'] - 60}
        except KeyError as err:
            print(new_token)
            raise
        os.makedirs(oauth_path.parent, exist_ok=True)
        with oauth_path.open('w') as fd:
            json.dump(token, fd)
        _expires = token['expires']
        _oauth_token = {'Authorization': 'Bearer {}'.format(token['access_token'])}
        return _oauth_token

