# ogs_api

I created this library to communicate with the APIs of online-go.com. 

This library is far from complete and not aimed to be used by others. It might be usefull for others as well, but it's mainly aimed to serve me, so the interface can change anytime.

Many functions will use/create a .cache folder.

## setup

You can provide credentials for OGS in 
`.settings/oauth_credentials.json`

```json
{
        "username": "...",
	"password": "...",
        "client_id": "...",
        "client_secret": "..."
}
```
client_id and client_secret are provided at https://online-go.com/oauth2/applications/
Each entry should be optional, the password is only needed once, to get the first oauth token. The API will ask for it when needed, so no need to store your password here.
