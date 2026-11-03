"""The router's model clients: BAML client names -> model ids, and the live gates."""
import re
from pathlib import Path

from iladub.route.models import MODEL_IDS, haiku_available, jev_available

CLIENTS = Path(__file__).resolve().parents[1] / "baml_src" / "clients.baml"


def _router_clients() -> dict[str, str]:
    text = CLIENTS.read_text()
    out = {}
    for m in re.finditer(r"client<llm>\s+(Router\w+)\s*\{(.*?)\n\}", text, re.S):
        model = re.search(r'model\s+"([^"]+)"', m.group(2))
        out[m.group(1)] = model.group(1)
    return out


def test_model_ids_match_clients_baml():
    clients = _router_clients()
    assert clients, "no Router* client found in clients.baml"
    assert set(clients) == set(MODEL_IDS)
    for name, model in clients.items():
        assert MODEL_IDS[name] == model
    assert MODEL_IDS["RouterHaiku"] == "claude-haiku-5-5"


def test_nothing_live_without_flag(monkeypatch):
    monkeypatch.delenv("BAML_LIVE", raising=False)
    assert haiku_available() is False
    assert jev_available() is False
