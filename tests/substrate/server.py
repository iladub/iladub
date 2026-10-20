"""Start/stop helpers for a local Fluree server (substrate:02). Plain module: the default suite
tests these without the real binary (spec 2026-10-20 § 4.2).

The readiness bound is an I/O bound (how long to wait for a socket), not a reading judgement.
"""
from __future__ import annotations

import contextlib
import itertools
import os
import shutil
import socket
import subprocess
import tempfile
import time
import uuid

import pytest

PINNED_VERSION = "fluree 4.2.4"
READY_BOUND_S = 30.0  # I/O bound on "is the port accepting"; decides nothing


def find_binary() -> str:
    path = os.environ.get("ILADUB_FLUREE_BIN") or shutil.which("fluree")
    if not path or not os.path.exists(path):
        pytest.fail("fluree binary not found: set ILADUB_FLUREE_BIN or put `fluree` on PATH "
                    f"(a selected substrate test never skips). looked for: {path!r}")
    return path


def check_version(binary: str) -> None:
    out = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=30)
    got = out.stdout.strip()
    if got != PINNED_VERSION:
        pytest.fail(f"the oracle is a claim about {PINNED_VERSION!r}; {binary} reports {got!r}")


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _accepts(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            return True
    except OSError:
        return False


def stop_server(proc: subprocess.Popen) -> None:
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@contextlib.contextmanager
def running_server(binary: str, ready_bound: float = READY_BOUND_S):
    """Yield (proc, base_url). Fails (never hangs, never skips) if the port is not accepting
    within ``ready_bound``, quoting the server's stderr. Terminates the process in ``finally``."""
    port = free_port()
    err = tempfile.TemporaryFile()
    proc = subprocess.Popen(
        [binary, "server", "run", "--memory", "--listen-addr", f"127.0.0.1:{port}"],
        stdout=subprocess.DEVNULL, stderr=err)
    try:
        deadline = time.monotonic() + ready_bound
        while not _accepts(port):
            if proc.poll() is not None or time.monotonic() >= deadline:
                why = (f"exited with {proc.returncode}" if proc.poll() is not None
                       else f"not accepting within {ready_bound}s")
                stop_server(proc)
                err.seek(0)
                pytest.fail(f"fluree server {why} on port {port}; stderr:\n"
                            f"{err.read().decode('utf-8', 'replace')}")
            time.sleep(0.1)
        yield proc, f"http://127.0.0.1:{port}"
    finally:
        stop_server(proc)
        err.close()


def ledger_namer():
    """A callable returning a distinct ledger name per call."""
    n = itertools.count()
    run = uuid.uuid4().hex[:8]
    return lambda: f"gate{run}n{next(n)}"
