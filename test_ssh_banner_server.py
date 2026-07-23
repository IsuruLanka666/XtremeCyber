"""Local banner server for testing XtremeCyber fingerprinting."""

from __future__ import annotations

import socket


HOST = "127.0.0.1"
PORT = 2222
BANNER = b"SSH-2.0-OpenSSH_9.6p1 XtremeCyber-Test\r\n"


def run_server() -> None:
    """Accept local connections and return a test SSH banner."""

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    ) as server:
        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )
        server.bind((HOST, PORT))
        server.listen(5)

        print(
            f"Test SSH banner server running on "
            f"{HOST}:{PORT}"
        )
        print("Press Ctrl+C to stop.")

        while True:
            client, address = server.accept()

            with client:
                print(f"Connection from {address}")
                client.sendall(BANNER)


if __name__ == "__main__":
    try:
        run_server()
    except KeyboardInterrupt:
        print("\nTest server stopped.")