import socket
import time
import traceback
import sys
import os
from typing import Callable
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from peer_manager import PeerManager
from protocol import make_message, make_leave
from network import Connection

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def ok(name: str) -> None:
    print(f"{GREEN}[PASS]{RESET} {name}")


def fail(name: str, e: str) -> None:
    print(f"{RED}[FAIL]{RESET} {name}")
    print(e)


def run_test(name: str, fn: Callable[[], None]) -> None:
    start = time.time()
    try:
        fn()
        ok(name)
    except Exception:
        fail(name, traceback.format_exc())
    print(f"⏱ {round(time.time() - start, 4)}s\n")


class MockSocket(socket.socket):
    def __init__(self) -> None:
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self._mock_closed = False

    def close(self) -> None:
        self._mock_closed = True
        try:
            super().close()
        except OSError:
            pass

    def recv(self, bufsize: int, flags: int = 0) -> bytes:
        return b""


class MockConnection(Connection):
    def __init__(self) -> None:
        super().__init__(MockSocket(), ("127.0.0.1", 12345))


def test_dedup() -> None:
    pm = PeerManager("A")

    c1 = MockConnection()
    c2 = MockConnection()

    pm.add_peer(c1)
    pm.add_peer(c2)

    m = make_message("A", "hello")

    pm.handle(c1, m)
    pm.handle(c2, m)

    assert len(pm.seen) == 1


def test_leave() -> None:
    pm = PeerManager("A")
    c = MockConnection()

    pm.add_peer(c)
    pm.handle(c, make_leave("A"))

    assert c not in pm.peers


def test_cleanup() -> None:
    pm = PeerManager("A")
    c = MockConnection()

    pm.add_peer(c)
    pm.remove_peer(c)

    assert c.alive is False
    assert getattr(c.sock, "_mock_closed", False) is True


def run() -> None:
    print("\n==============================")
    print("   TuTalk Test Pipeline")
    print("==============================\n")

    run_test("Message deduplication", test_dedup)
    run_test("Leave propagation", test_leave)
    run_test("Connection cleanup", test_cleanup)

    print("==============================")
    print("   PIPELINE DONE")
    print("==============================\n")


if __name__ == "__main__":
    run()
