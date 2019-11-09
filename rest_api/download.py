#!/usr/bin/python3

_sleep_if_throttled = 60

def access_api(url, params={}, debug=False):
    import requests
    from time import sleep
    from ogs_api.access_tokens import get_oauth_token
    oauth_token = get_oauth_token()
    url = 'https://online-go.com{}'.format(url)
    while True:
        req = requests.get(url, headers=oauth_token, params=params)
        if not req.ok:
            if req.status_code == 520:
                print('got status_code {status_code} for {url}'.format(url=req.url, status_code=req.status_code))
                sleep(_sleep_if_throttled)
                continue
            elif req.status_code == 429:
                if debug:
                    print('got status_code {status_code} for {url}. Request was throttled'.format(url=req.url, status_code=req.status_code))
                sleep(_sleep_if_throttled)
                continue
            elif req.status_code == 525:
                if debug:
                    print('got status_code {status_code} for {url}. '.format(url=req.url, status_code=req.status_code))
                continue
            elif req.status_code == 502:
                if debug:
                    print('got status_code {status_code} for {url}. '.format(url=req.url, status_code=req.status_code))
                sleep(_sleep_if_throttled)
                continue
            elif req.status_code == 404:
                print('got status_code {status_code} for {url}. '.format(url=req.url, status_code=req.status_code))
                return None
            else:
                print('got status_code {status_code} for {url}'.format(url=req.url, status_code=req.status_code))
                sleep(_sleep_if_throttled)
                continue
                #raise ConnectionError('got status_code {status_code} for {url}'.format(url=req.url, status_code=req.status_code))
        j = req.json()
        if 'detail' in j and j['detail'] == 'Request was throttled.':
            if debug:
                print('Throteled', url)
            sleep(_sleep_if_throttled)
            continue
        else:
            return j


