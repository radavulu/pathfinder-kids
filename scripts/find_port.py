#!/usr/bin/env python3
"""Print the first available TCP port on host, starting from the app default."""
from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.config import DEFAULT_PORT  # noqa: E402


def find_port(host: str, start: int, count: int = 20) -> int:
    for port in range(start, start + count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError:
                continue
            return port
    print(
        f"No free port on {host} in range {start}-{start + count - 1}. "
        f"Stop the other process or set HOMEKUMON_PORT.",
        file=sys.stderr,
    )
    raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--start", type=int, default=DEFAULT_PORT)
    parser.add_argument("--count", type=int, default=20)
    args = parser.parse_args()
    print(find_port(args.host, args.start, args.count))


if __name__ == "__main__":
    main()
