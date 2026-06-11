import threading
import logging
from typing import List, Set, Dict, Any, Optional
from network import Connection
from protocol import encode, decode, MessageType

logger = logging.getLogger(__name__)

MAX_LINE_LENGTH = 65536


class PeerManager:
    def __init__(self, username: str):
        self.username = username
        self.peers: List[Connection] = []
        self.seen: Set[str] = set()

        self._peers_lock = threading.Lock()
        self._seen_lock = threading.Lock()

    def add_peer(self, conn: Connection) -> None:
        with self._peers_lock:
            self.peers.append(conn)
        threading.Thread(target=self._listen_loop, args=(conn,), daemon=True).start()

    def remove_peer(self, conn: Connection) -> None:
        with self._peers_lock:
            if conn in self.peers:
                self.peers.remove(conn)
        conn.close()

    def broadcast(self, msg: Dict[str, Any]) -> None:
        data = encode(msg)
        with self._peers_lock:
            current_peers = list(self.peers)

        for p in current_peers:
            try:
                p.send(data)
            except OSError:
                self.remove_peer(p)

    def _listen_loop(self, conn: Connection) -> None:
        buffer = ""
        while conn.alive:
            try:
                data = conn.sock.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                if len(buffer) > MAX_LINE_LENGTH and "\n" not in buffer[:MAX_LINE_LENGTH]:
                    logger.error(f"Protocol violation from {conn.addr}: line too long.")
                    break

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        msg = decode(line)
                        self.handle(conn, msg)
                    except Exception as e:
                        logger.error(f"Failed to decode message: {e}")

            except (OSError, UnicodeDecodeError):
                break

        self.remove_peer(conn)

    def handle(self, conn: Optional[Connection], msg: Dict[str, Any]) -> None:
        mid = msg.get("id")
        if mid:
            with self._seen_lock:
                if mid in self.seen:
                    return
                self.seen.add(mid)

        t = msg.get("type")
        sender = msg.get("sender", "Unknown")

        if t == MessageType.MESSAGE.value:
            print(f"\n💬 {sender}: {msg.get('content', '')}")
            self.broadcast(msg)

        elif t == MessageType.HELLO.value:
            print(f"\n🔗 {sender} joined the network")

        elif t == MessageType.LEAVE.value:
            print(f"\n👋 {sender} left the chat")
            if conn:
                self.remove_peer(conn)