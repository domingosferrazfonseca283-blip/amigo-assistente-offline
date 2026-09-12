from __future__ import annotations

from intelligence.router import ModelRouter, ModelUnavailableError


class Working:
    def __init__(self, value: str):
        self.value = value

    def generate(self, prompt: str) -> str:
        return self.value


class Broken:
    def generate(self, prompt: str) -> str:
        raise ModelUnavailableError("offline")


def test_router_prefers_local_model():
    router = ModelRouter(local=Working("local"), online=Working("online"))
    assert router.generate("olá") == "local"


def test_router_falls_back_to_explicit_online_model():
    router = ModelRouter(local=Broken(), online=Working("online"))
    assert router.generate("olá") == "online"


def test_router_fails_explicitly_without_models():
    router = ModelRouter()
    try:
        router.generate("olá")
    except ModelUnavailableError as exc:
        assert "nenhum backend configurado" in str(exc)
    else:
        raise AssertionError("esperava ModelUnavailableError")
