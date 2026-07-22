"""
Multithreaded TCP connect scanning engine.

"""

from __future__ import annotations

import errno
import ipaddress
import queue
import socket
import threading
import time
from collections.abc import Callable, Iterator

from core.exceptions import ValidationError
from core.logger import get_logger
from core.scanning.models import ScanConfiguration, TargetKind
from core.scanning.results import (
    PortScanResult,
    PortState,
    ScanProgress,
    ScanSummary,
)
from core.scanning.services import collect_banner, service_name
from core.scanning.targets import resolve_target


logger = get_logger(__name__)

ResultCallback = Callable[[PortScanResult], None]
ProgressCallback = Callable[[ScanProgress], None]
StatusCallback = Callable[[str], None]


class ScanEngine:
    """Bounded multithreaded TCP connect scanner."""

    def __init__(
        self,
        configuration: ScanConfiguration,
        *,
        result_callback: ResultCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        status_callback: StatusCallback | None = None,
        max_operations: int = 200_000,
        banner_max_bytes: int = 256,
    ) -> None:
        self.configuration = configuration
        self.result_callback = result_callback
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.max_operations = max(1, int(max_operations))
        self.banner_max_bytes = max(0, int(banner_max_bytes))

        self._cancel_event = threading.Event()
        self._lock = threading.Lock()

        self._completed = 0
        self._open_ports = 0
        self._closed_ports = 0
        self._errors = 0

    def cancel(self) -> None:
        """Request cooperative cancellation."""

        self._cancel_event.set()
        self._emit_status("Cancelling scan...")

    @property
    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def run(self) -> ScanSummary:
        """Run the configured scan synchronously."""

        started_at = time.perf_counter()

        hosts = self._prepare_hosts()
        ports = tuple(self.configuration.ports)
        total = len(hosts) * len(ports)

        if total <= 0:
            raise ValidationError(
                "The scan configuration does not contain any operations."
            )

        if total > self.max_operations:
            raise ValidationError(
                f"This scan would perform {total:,} TCP checks. "
                f"The configured safety limit is {self.max_operations:,}. "
                "Reduce the target range or port selection."
            )

        self._emit_status(
            f"Starting TCP scan: {len(hosts)} host(s), "
            f"{len(ports)} port(s), {total:,} checks."
        )
        self._emit_progress(total)

        task_queue: queue.Queue[tuple[str, int] | None] = queue.Queue(
            maxsize=max(8, self.configuration.max_workers * 4)
        )

        workers = [
            threading.Thread(
                target=self._worker_loop,
                args=(task_queue, total),
                name=f"xtremecyber-scan-{index + 1}",
                daemon=True,
            )
            for index in range(self.configuration.max_workers)
        ]

        for worker in workers:
            worker.start()

        try:
            for task in self._tasks(hosts, ports):
                if self._cancel_event.is_set():
                    break

                while not self._cancel_event.is_set():
                    try:
                        task_queue.put(task, timeout=0.1)
                        break
                    except queue.Full:
                        continue
        finally:
            for _ in workers:
                placed = False

                while not placed:
                    try:
                        task_queue.put(None, timeout=0.1)
                        placed = True
                    except queue.Full:
                        if not any(worker.is_alive() for worker in workers):
                            placed = True

            for worker in workers:
                worker.join()

        duration = time.perf_counter() - started_at

        with self._lock:
            summary = ScanSummary(
                total=total,
                completed=self._completed,
                open_ports=self._open_ports,
                closed_ports=self._closed_ports,
                errors=self._errors,
                cancelled=self._cancel_event.is_set(),
                duration_seconds=duration,
            )

        self._emit_progress(total)

        if summary.cancelled:
            self._emit_status(
                f"Scan cancelled after {summary.completed:,} of "
                f"{summary.total:,} checks."
            )
        else:
            self._emit_status(
                f"Scan complete: {summary.open_ports} open, "
                f"{summary.closed_ports} closed, "
                f"{summary.errors} error(s)."
            )

        logger.info(
            "TCP scan finished: total=%s completed=%s open=%s closed=%s "
            "errors=%s cancelled=%s duration=%.3f",
            summary.total,
            summary.completed,
            summary.open_ports,
            summary.closed_ports,
            summary.errors,
            summary.cancelled,
            summary.duration_seconds,
        )

        return summary

    def _prepare_hosts(self) -> tuple[str, ...]:
        target = self.configuration.target

        if (
            target.kind == TargetKind.HOSTNAME
            and self.configuration.resolve_hostname
        ):
            self._emit_status(
                f"Resolving hostname {target.normalized_value}..."
            )
            return resolve_target(target).addresses

        return target.hosts

    def _tasks(
        self,
        hosts: tuple[str, ...],
        ports: tuple[int, ...],
    ) -> Iterator[tuple[str, int]]:
        for host in hosts:
            for port in ports:
                yield host, port

    def _worker_loop(
        self,
        task_queue: queue.Queue[tuple[str, int] | None],
        total: int,
    ) -> None:
        while True:
            task = task_queue.get()

            try:
                if task is None:
                    return

                host, port = task

                if self._cancel_event.is_set():
                    return

                result = self._probe(host, port)
                self._record_result(result, total)
            finally:
                task_queue.task_done()

    def _probe(
        self,
        host: str,
        port: int,
    ) -> PortScanResult:
        started_at = time.perf_counter()
        connected_socket: socket.socket | None = None

        try:
            connected_socket = socket.create_connection(
                (host, port),
                timeout=self.configuration.timeout_seconds,
            )
            latency_ms = (time.perf_counter() - started_at) * 1000

            try:
                peer_address = str(connected_socket.getpeername()[0])
            except OSError:
                peer_address = host

            banner = ""

            if self.configuration.banner_grab:
                banner = collect_banner(
                    connected_socket,
                    host=host,
                    port=port,
                    timeout_seconds=self.configuration.timeout_seconds,
                    max_bytes=self.banner_max_bytes,
                )

            return PortScanResult(
                host=host,
                resolved_address=peer_address,
                port=port,
                state=PortState.OPEN,
                service=service_name(port),
                banner=banner,
                latency_ms=round(latency_ms, 2),
            )

        except ConnectionRefusedError:
            return PortScanResult(
                host=host,
                port=port,
                state=PortState.CLOSED,
                service=service_name(port),
                error="connection refused",
            )

        except socket.timeout:
            return PortScanResult(
                host=host,
                port=port,
                state=PortState.ERROR,
                service=service_name(port),
                error="connection timed out",
            )

        except OSError as exc:
            state = (
                PortState.CLOSED
                if exc.errno in {
                    errno.ECONNREFUSED,
                    errno.ECONNRESET,
                }
                else PortState.ERROR
            )

            return PortScanResult(
                host=host,
                port=port,
                state=state,
                service=service_name(port),
                error=str(exc),
            )

        finally:
            if connected_socket is not None:
                try:
                    connected_socket.close()
                except OSError:
                    pass

    def _record_result(
        self,
        result: PortScanResult,
        total: int,
    ) -> None:
        with self._lock:
            self._completed += 1

            if result.state == PortState.OPEN:
                self._open_ports += 1
            elif result.state == PortState.CLOSED:
                self._closed_ports += 1
            else:
                self._errors += 1

            progress = ScanProgress(
                completed=self._completed,
                total=total,
                open_ports=self._open_ports,
                closed_ports=self._closed_ports,
                errors=self._errors,
                cancelled=self._cancel_event.is_set(),
            )

        if self.result_callback is not None:
            self.result_callback(result)

        if self.progress_callback is not None:
            self.progress_callback(progress)

    def _emit_progress(self, total: int) -> None:
        if self.progress_callback is None:
            return

        with self._lock:
            progress = ScanProgress(
                completed=self._completed,
                total=total,
                open_ports=self._open_ports,
                closed_ports=self._closed_ports,
                errors=self._errors,
                cancelled=self._cancel_event.is_set(),
            )

        self.progress_callback(progress)

    def _emit_status(self, message: str) -> None:
        if self.status_callback is not None:
            self.status_callback(message)
