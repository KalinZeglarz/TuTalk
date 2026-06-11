import threading

from network import Listener, connect_to_peer
from peer_manager import PeerManager
from protocol import make_message, make_hello, make_leave, encode


def run_chat(manager):
    print("\n💬 Type /quit to leave\n")

    listener_thread = threading.Thread(target=input_loop, args=(manager,))
    listener_thread.start()
    listener_thread.join()

    # SEND LEAVE EVENT
    manager.broadcast(make_leave(manager.username))

    print("\n↩ Returning to main menu...\n")


def input_loop(manager):
    while True:
        msg = input("> ").strip()

        if msg == "/quit":
            break

        if msg:
            manager.handle(None, make_message(manager.username, msg))


def main():
    while True:
        print("\n====================")
        print(" TuTalk MENU")
        print("====================")
        print("1. Start chat")
        print("2. Exit")

        choice = input("> ").strip()

        if choice == "2":
            break

        username = input("Username: ")
        port = int(input("Port: "))

        peers = []

        while True:
            p = input("Peer ip:port (ENTER to continue): ").strip()
            if not p:
                break
            host, port_p = p.split(":")
            peers.append((host, int(port_p)))

        manager = PeerManager(username)

        Listener("0.0.0.0", port, manager.add_peer).start()

        for h, p in peers:
            conn = connect_to_peer(h, p)
            if conn:
                manager.add_peer(conn)
                conn.send(encode(make_hello(username)))

        run_chat(manager)


if __name__ == "__main__":
    main()
