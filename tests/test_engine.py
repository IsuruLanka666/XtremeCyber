"""
Local-loopback tests for the TCP scanning engine.
"""

from __future__ import annotations

import socket
import threading
import unittest

from core.scanning.engine import ScanEngine
from core.scanning.models import (
    ScanConfiguration,
    ScanProfile,
)
from core.scanning.ports import parse_port_spec
from core.scanning.results import PortState
from core.scanning.targets import parse_target


class LocalServer:
    def __init__(self) -> None:
        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )
        self.socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )
        self.socket.bind(("127.0.0.1", 0))
        self.socket.listen(5)
        self.socket.settimeout(0.2)
        self.port = int(self.socket.getsockname()[1])
        self.stop_event = threading.Event()
        self.thread = threading.Thread(
            target=self._serve,
            daemon=True,
        )

    def start(self) -> None:
        self.thread.start()

    def close(self) -> None:
        self.stop_event.set()

        try:
            socket.create_connection(
                ("127.0.0.1", self.port),
                timeout=0.1,
            ).close()
        except OSError:
            pass

        self.thread.join(timeout=1)
        self.socket.close()

    def _serve(self) -> None:
        while not self.stop_event.is_set():
            try:
                client, _ = self.socket.accept()
            except socket.timeout:
                continue
            except OSError:
                return

            with client:
                try:
                    client.sendall(b"XtremeCyber test service\r\n")
                except OSError:
                    pass


class ScanEngineTests(unittest.TestCase):
    def test_loopback_open_port(self) -> None:
        server = LocalServer()
        server.start()

        results = []

        try:
            configuration = ScanConfiguration(
                target=parse_target("127.0.0.1"),
                ports=parse_port_spec(str(server.port)),
                profile=ScanProfile.CUSTOM,
                max_workers=4,
                timeout_seconds=1.0,
                banner_grab=True,
                resolve_hostname=True,
                authorization_confirmed=True,
            )

            engine = ScanEngine(
                configuration,
                result_callback=results.append,
                max_operations=10,
            )

            summary = engine.run()
        finally:
            server.close()

        self.assertEqual(summary.open_ports, 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].state, PortState.OPEN)
        self.assertIn("XtremeCyber test service", results[0].banner)

    def test_operation_limit(self) -> None:
        configuration = ScanConfiguration(
            target=parse_target("127.0.0.1"),
            ports=parse_port_spec("1-20"),
            profile=ScanProfile.CUSTOM,
            max_workers=2,
            timeout_seconds=0.1,
            banner_grab=False,
            resolve_hostname=False,
            authorization_confirmed=True,
        )

        engine = ScanEngine(
            configuration,
            max_operations=10,
        )

        with self.assertRaises(Exception):
            engine.run()


if __name__ == "__main__":
    unittest.main()
