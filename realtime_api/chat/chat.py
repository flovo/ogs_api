from ogs_api.realtime_api.socket import comm_socket

"""
possible chat events emitted by the server are:
 -  "chat-message": 
 -  "chat-message-removed":
 -  "chat-join":
 -  "chat-part": 
"""


def _chat_connect():
    from ogs_api.access_tokens import get_data, get_chat_auth
    data = get_data()
    comm_socket.emit("chat/connect", data={"auth": get_chat_auth(),
                                           "player_id": data["user"]["id"],
                                           "ranking": data["user"]["ranking"],
                                           "username": data["user"]["username"],
                                           "ui_class": data["user"]["ui_class"]})


comm_socket.on("connect", _chat_connect)


def chat_join(channel: str):
    comm_socket.emit("chat/join", data={"channel": channel})

