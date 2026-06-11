import pytest

@pytest.fixture
def generic_env(monkeypatch):
    monkeypatch.setenv("SteamApiKey", "S6S5H56HTS3TLS3S68TH4S6T56G56S5G")
    monkeypatch.setenv("SteamID", "11321321tashta321")
    yield