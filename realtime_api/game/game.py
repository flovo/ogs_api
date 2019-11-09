from ogs_api.realtime_api.socket import comm_socket
from ogs_api.access_tokens import get_data


def game_connect(game_id, connect_to_gamechat=0):
    data = get_data()
    comm_socket.emit("game/connect", data={"game_id": game_id,
                                           "player_id": data["user"]["id"],
                                           "chat": connect_to_gamechat})


def game_disconnect(game_id):
    comm_socket.emit("game/disconnect", data={"game_id": game_id})


def _num2char(num: int) -> str:
    if num == -1:
        return "."
    return "abcdefghijklmnopqrstuvwxyz"[num]


def game_pass(game_id):
    data = get_data()
    comm_socket.emit("game/move", data={"game_id": game_id,
                                        "player_id": data["user"]["id"],
                                        "move": ".."})


def game_resume(game_id):
    data = get_data()
    comm_socket.emit("game/resume", data={"game_id": game_id,
                                          "player_id": data["user"]["id"]})


def game_chat(game_id, message, move_number, type="main"):
    data = get_data()
    comm_socket.emit("game/chat", data={"game_id": game_id,
                                        "player_id": data["user"]["id"],
                                        "type": type,
                                        "body": message,
                                        "move_number": move_number
                                        })


def add_game_handler(game_id, type, handler):
    comm_socket.on("game/{game_id}/{type}".format(game_id=game_id, type=type), handler=handler)


def add_game_move_handler(game_id, handler):
    add_game_handler(game_id, "move", handler)


def add_game_clock_handler(game_id, handler):
    add_game_handler(game_id, "clock", handler)


def add_game_undo_requested_handler(game_id, handler):
    add_game_handler(game_id, "undo_requested", handler)

