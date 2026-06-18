"""BAML toolchain walking-skeleton smoke test (Transplant M4, Task 1).

Deviation from the original plan: the plan targets ``baml_client.b``, but in the
installed BAML (baml-py / baml-cli 0.222.0) the top-level ``baml_client.b`` is the
*async* client (``from .async_client import b``). Its ``PingExtract`` is a coroutine
function, so the plan's synchronous test pattern (plain-lambda monkeypatch, direct
call, assert on ``result.ok``) does not work against it. The *synchronous* client is
exposed at ``baml_client.sync_client.b``; that is what these tests target.
"""

import os

import pytest


def test_baml_client_imports():
    from baml_client.sync_client import b  # noqa: F401
    from baml_client.types import Ping  # noqa: F401


def test_ping_offline(monkeypatch):
    from baml_client.types import Ping
    from baml_client import sync_client

    monkeypatch.setattr(
        sync_client.b,
        "PingExtract",
        lambda text: Ping(ok=True, echo=text),
        raising=True,
    )
    result = sync_client.b.PingExtract("hello")
    assert result.ok is True
    assert result.echo == "hello"


@pytest.mark.skipif(
    os.environ.get("BAML_LIVE") != "1",
    reason="set BAML_LIVE=1 to call the real API",
)
def test_ping_live():
    from baml_client.sync_client import b

    result = b.PingExtract("hello")
    assert result.ok is True
