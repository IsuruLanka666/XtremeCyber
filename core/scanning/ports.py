"""TCP port specification parsing and normalization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

from core.exceptions import ValidationError

MIN_PORT = 1
MAX_PORT = 65535


@dataclass(frozen=True, order=True, slots=True)
class PortRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if not MIN_PORT <= self.start <= MAX_PORT:
            raise ValidationError(f"Port {self.start} is outside the valid range 1-65535.")
        if not MIN_PORT <= self.end <= MAX_PORT:
            raise ValidationError(f"Port {self.end} is outside the valid range 1-65535.")
        if self.start > self.end:
            raise ValidationError(f"Invalid port range {self.start}-{self.end}.")

    @property
    def count(self) -> int:
        return self.end - self.start + 1

    def __iter__(self) -> Iterator[int]:
        return iter(range(self.start, self.end + 1))

    def __str__(self) -> str:
        return str(self.start) if self.start == self.end else f"{self.start}-{self.end}"


@dataclass(frozen=True, slots=True)
class PortSpec:
    ranges: tuple[PortRange, ...]

    def __post_init__(self) -> None:
        if not self.ranges:
            raise ValidationError("At least one TCP port is required.")

    @property
    def count(self) -> int:
        return sum(port_range.count for port_range in self.ranges)

    @property
    def normalized(self) -> str:
        return ",".join(str(port_range) for port_range in self.ranges)

    def __iter__(self) -> Iterator[int]:
        for port_range in self.ranges:
            yield from port_range


def parse_port_spec(value: str) -> PortSpec:
    """Parse expressions such as 80, 20-25, or 22,80,443."""

    text = value.strip()
    if not text:
        raise ValidationError("Enter at least one TCP port.")

    ranges: list[PortRange] = []

    for token in text.split(","):
        token = token.strip()
        if not token:
            raise ValidationError("The port specification contains an empty value.")

        if token.isdigit():
            port = _parse_port_number(token)
            ranges.append(PortRange(port, port))
            continue

        if token.count("-") != 1:
            raise ValidationError(f"Invalid port expression '{token}'.")

        start_text, end_text = (part.strip() for part in token.split("-", maxsplit=1))
        if not start_text.isdigit() or not end_text.isdigit():
            raise ValidationError(f"Invalid port range '{token}'.")

        ranges.append(PortRange(_parse_port_number(start_text), _parse_port_number(end_text)))

    return PortSpec(tuple(_merge_ranges(ranges)))


def _parse_port_number(value: str) -> int:
    port = int(value)
    if not MIN_PORT <= port <= MAX_PORT:
        raise ValidationError(f"Port {port} is outside the valid range 1-65535.")
    return port


def _merge_ranges(ranges: list[PortRange]) -> list[PortRange]:
    ordered = sorted(ranges, key=lambda item: (item.start, item.end))
    merged: list[PortRange] = []

    for current in ordered:
        if not merged:
            merged.append(current)
            continue

        previous = merged[-1]
        if current.start <= previous.end + 1:
            merged[-1] = PortRange(previous.start, max(previous.end, current.end))
        else:
            merged.append(current)

    return merged
