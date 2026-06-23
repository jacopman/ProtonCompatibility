import os

from dotenv import load_dotenv
import pytest
import requests
import func


class TestDotEnv:
    def test_empty_env_returns_empty_dict(self, monkeypatch, httpserver):
        monkeypatch.delenv("SteamApiKey", "")
        monkeypatch.delenv("SteamID", "")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        assert not func.get_steam_library(STEAM_API_KEY, STEAM_ID)

    def test_invalid_steamApiKey_returns_empty_dict(self, monkeypatch, httpserver):
        monkeypatch.setenv("SteamApiKey", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        assert not func.get_steam_library(STEAM_API_KEY, STEAM_ID)

    def test_invalid_steamID_returns_empty_dict(self, monkeypatch):
        monkeypatch.setenv("SteamID", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        assert not func.get_steam_library(STEAM_API_KEY, STEAM_ID)

    def test_invalid_credentials_returns_empty_dict(self, monkeypatch):
        monkeypatch.setenv("SteamApiKey", "invalid_api_key")
        monkeypatch.setenv("SteamID", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        assert not func.get_steam_library(STEAM_API_KEY, STEAM_ID)

    def test_valid_credentials_returns_non_empty_dict(self, httpserver):
        mock_steam_response = {
            "response": {
                "game_count": 2,
                "games": [
                    {"appid": 400, "name": "Portal"},
                    {"appid": 220, "name": "Half-Life 2"}
                ]
            }
        }
        httpserver.expect_request(
            "/IPlayerService/GetOwnedGames/v0001/",
            query_string=None  # This explicitly tells the server to ignore whatever query parameters are sent
        ).respond_with_json(mock_steam_response)
        load_dotenv()
        # STEAM_ID = os.getenv("SteamID")
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamId")
        base_url = httpserver.url_for("")
        result =  func.get_steam_library(STEAM_API_KEY, STEAM_ID, base_url = base_url)
        assert result == {400: "Portal", 220: "Half-Life 2"}