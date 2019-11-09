#!/usr/bin/python3

import socketio
from ogs_api.access_tokens import get_chat_auth, get_user_jwt, get_data
from collections import defaultdict

repetition_accuracy = 1.0


class OGSCommSocket:
    handlers = defaultdict(list)
    repeated_tasks = set()
    comm_socket = socketio.Client(reconnection_delay_max=60, logger=False, engineio_logger=False)
    clock_drift = 0.0
    clock_latency = 0.0
    last_ping = 0
    last_issued_ping = 0

    def connect(self):
        if not self.comm_socket.connected:
            self.comm_socket.connect("https://online-go.com/socket.io/?EIO=3", transports='websocket')

    def disconnect(self):
        if self.comm_socket.connected:
            self.comm_socket.disconnect()

    def exit(self):
        self.disconnect()
        for thread, stop_event in self.repeated_tasks:
            stop_event.set()

    def emit(self, event, data=None, namespace=None, callback=None):
        self.comm_socket.emit(event=event, data=data, namespace=namespace, callback=callback)

    def sleep(self, seconds=0):
        self.comm_socket.sleep(seconds=seconds)

    def on(self, key, handler):
        if key not in self.handlers:
            def _handler(*args, **kwargs):
                self._on_event(key, *args, **kwargs)
            self.comm_socket.on(key, handler=_handler)
        if handler not in self.handlers.values():
            self.handlers[key].append(handler)
            if key == "connect" and self.comm_socket.connected:
                handler()

    def remove_handler(self, key, handler):
        self.handlers[key].remove(handler)

    def _on_event(self, key, *args, **kwargs):
        for handler in self.handlers[key]:
            handler(*args, **kwargs)

    def start_background_task(self, target, *args, **kwargs):
        return self.comm_socket.start_background_task(target, *args, **kwargs)

    def start_repeated_background_task(self, func, interval, *args, **kwargs):
        from threading import Event
        from time import time
        stop = Event()

        def repeated_background_task():
            last_run = 0
            while not stop.wait(repetition_accuracy):
                if (time() - last_run >= interval) and self.comm_socket.connected:
                    self.start_background_task(func, *args, **kwargs)
                    last_run = time()
        thread = self.start_background_task(repeated_background_task)
        self.repeated_tasks.add((thread, stop))
        return thread, stop

    def ping(self):
        from time import time
        self.last_issued_ping = max(self.last_issued_ping, time())
        self.emit("net/ping", {"client": int(time() * 1000), "drift": self.clock_drift, "latency": self.clock_latency})

    def __init__(self):
        def authenticate():
            data = get_data()
            self.emit("authenticate", data={"auth": get_chat_auth(),
                                            "player_id": data["user"]["id"],
                                            "username": data["user"]["username"],
                                            "jwt": get_user_jwt()})
        self.on("connect", handler=authenticate)

        def handle_pong(msg):
            from time import time
            now = time() * 1000
            latency = now - msg["client"]
            drift = ((now - latency / 2) - msg["server"])
            self.clock_latency = latency / 1000
            self.clock_drift = drift / 1000
            self.last_ping = now / 1000
        self.on("net/pong", handler=handle_pong)

        self.start_repeated_background_task(self.ping, 10.0)

        def on_HUP():
            """reload"""
            self.disconnect()
            self.sleep(1)
            self.connect()
        self.on("HUP", handler=on_HUP)

    def __del__(self):
        self.exit()


comm_socket = OGSCommSocket()
comm_socket.connect()
