import socket
import threading
import logging
from typing import Tuple, Callable, Optional

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, sock: socket.socket, addr: Tuple[str, int]):
        self.sock = sock
        self.addr = addr
        self.alive = True

    def send(self, data: bytes) -> None:
        if not self.alive:
            return
        try:
            self.sock.sendall(data)
        except OSError as e:
            logger.error(f"Failed to send data to {self.addr}: {e}")
            self.alive = False
            raise

    def close(self) -> None:
        self.alive = False
        try:
            self.sock.close()
        except OSError:
            pass


class Listener(threading.Thread):
    def __init__(self, host: str, port: int, on_connect: Callable[[Connection], None]):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        self.on_connect = on_connect
        self._running = True
        self.server_sock: Optional[socket.socket] = None

    def run(self) -> None:
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_sock.bind((self.host, self.port))
            self.server_sock.listen()
            logger.info(f"📡 Listening on {self.host}:{self.port}")
        except OSError as e:
            logger.error(f"Failed to bind to {self.host}:{self.port}: {e}")
            return

        while self._running:
            try:
                client, addr = self.server_sock.accept()
                self.on_connect(Connection(client, addr))
            except OSError:
                break


def connect_to_peer(host: str, port: int) -> Optional[Connection]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(180.0)
        s.connect((host, port))
        s.settimeout(None)
        return Connection(s, (host, port))
    except OSError as e:
        logger.warning(f"❌ {host}:{port} Not connected: {e}")
        return None
