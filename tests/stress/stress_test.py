import socket
import sys
import os
import time
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from peer_manager import PeerManager
from protocol import make_message
from network import Connection


class FakeSock(socket.socket):
    """Mock socket zgodny z sygnaturami i typowaniem klasy socket.socket pod Windows."""

    def __init__(self) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._mock_closed = False

    def send(self, data: bytes, flags: int = 0) -> int:
        return len(data)

    def sendall(self, data: bytes, flags: int = 0) -> None:
        return None

    def close(self) -> None:
        self._mock_closed = True
        try:
            super().close()
        except OSError:
            pass

    def recv(self, bufsize: int, flags: int = 0) -> bytes:
        while not self._mock_closed:
            time.sleep(0.1)
        return b""


class FakeConn(Connection):

    def __init__(self) -> None:
        super().__init__(FakeSock(), ("127.0.0.1", 5000))
        self.sent: list[bytes] = []

    def send(self, data: bytes) -> None:
        self.sent.append(data)
        super().send(data)


def test_stress() -> None:
    print("\n🔥 STRESS TEST: P2P mesh simulation\n")

    pm = PeerManager("A")
    peers = [FakeConn() for _ in range(10)]

    for p in peers:
        pm.add_peer(p)

    start = time.time()

    for i in range(50):
        msg = make_message("B", f"msg-{i}")
        try:
            pm.handle(peers[0], msg)
        except Exception:
            pass

    duration = time.time() - start

    with pm._peers_lock:
        current_peer_count = len(pm.peers)

    with pm._seen_lock:
        current_seen_count = len(pm.seen)

    print(f"Messages processed: 50")
    print(f"Peers: {current_peer_count}")
    print(f"Seen dedup size: {current_seen_count}")
    print(f"Time: {round(duration, 4)}s")

    assert current_peer_count == 10, f"Expected 10 peers, got {current_peer_count}"
    assert current_seen_count == 50, f"Expected 50 seen messages, got {current_seen_count}"

    print("\n✅ STRESS TEST PASSED\n")


if __name__ == "__main__":
    test_stress()
