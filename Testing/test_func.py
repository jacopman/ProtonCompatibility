import os

from dotenv import load_dotenv
import httpx
import pytest
import respx
import func
from unittest.mock import AsyncMock, patch


class TestSteamLibraryCalls:
    def test_empty_env_returns_empty_dict(self, monkeypatch):
        # setup
        monkeypatch.delenv("SteamApiKey", "")
        monkeypatch.delenv("SteamID", "")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")

        # function run
        result = func.get_steam_library(STEAM_API_KEY, STEAM_ID)

        # assert
        assert not result

    def test_invalid_steamApiKey_returns_empty_dict(self, monkeypatch):
        monkeypatch.setenv("SteamApiKey", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        # function run
        result = func.get_steam_library(STEAM_API_KEY, STEAM_ID)
        # assert
        assert not result

    def test_invalid_steamID_returns_empty_dict(self, monkeypatch):
        monkeypatch.setenv("SteamID", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        # function run
        result = func.get_steam_library(STEAM_API_KEY, STEAM_ID)
        # assert
        assert not result

    def test_invalid_credentials_returns_empty_dict(self, monkeypatch):
        monkeypatch.setenv("SteamApiKey", "invalid_api_key")
        monkeypatch.setenv("SteamID", "invalid_api_key")
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamID")
        # function run
        result = func.get_steam_library(STEAM_API_KEY, STEAM_ID)
        # assert
        assert not result

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
            "/IPlayerService/GetOwnedGames/v0001/"
        ).respond_with_json(mock_steam_response)
        load_dotenv()
        STEAM_API_KEY = os.getenv("SteamApiKey")
        STEAM_ID = os.getenv("SteamId")
        base_url = httpserver.url_for("")
        result =  func.get_steam_library(STEAM_API_KEY, STEAM_ID, base_url = base_url)
        assert result == {400: "Portal", 220: "Half-Life 2"}

@pytest.mark.asyncio
class TestProtonCompatibility:
    _appid = "11111"
    _url = f"https://www.protondb.com/api/v1/reports/summaries/11111.json"

    @respx.mock
    async def test_check_proton_compatibility_success(self):
        respx.get(self._url).mock(return_value=httpx.Response(200, json={"tier": "gold"}))
        result = await func.check_proton_compatibility(self._appid)
        assert result == "gold"
    
    @respx.mock
    async def test_check_proton_compatibility_404_native(self):
        respx.get(self._url).mock(return_value=httpx.Response(404))

        result = await func.check_proton_compatibility(self._appid)
        assert result == "unknown/native"

    @respx.mock
    async def test_check_proton_compatibility_missing_tier_key(self):
        respx.get(self._url).mock(return_value=httpx.Response(200, json={"results": "green"}))

        result = await func.check_proton_compatibility(self._appid)
        assert result == "unknown"
    
    @respx.mock
    async def test_check_proton_compatibility_http_error(self):
        respx.get(self._url).mock(return_value=httpx.Response(500))
        result = await func.check_proton_compatibility(self._appid)
        assert result == "Error"

    @respx.mock
    async def test_check_proton_compatibility_timeout(self):
        respx.get(self._url).mock(side_effect=httpx.ConnectTimeout("Connection timed out"))

        result = await func.check_proton_compatibility(self._appid)
        
        assert result == "Error"

@pytest.mark.asyncio
class TestFilterGamesByTier:

    @pytest.fixture
    def sample_games(self):
        return {
        12345: "Game One",
        67890: "Game Two",
        11111: "Game Three",
        22222: "Game Four",
    }

    @pytest.fixture
    def mock_check_proton(self):
        with patch("func.check_proton_compatibility") as mock:
            yield mock

    @pytest.fixture
    def mock_sleep(self):
        with patch("func.asyncio.sleep", new_callable=AsyncMock) as mock:
            yield mock

    async def test_filter__incompatibile(self,mock_check_proton, sample_games):
        games = sample_games
        mock_check_proton.side_effect = lambda appid: "borked" if appid == "12345" or appid == "11111" else "gold"

        result = await func.filter_games_by_tier(games, "Incompatible")

        expected = [
            ("Game One", "12345", "Borked(Incompatible)"),
            ("Game Three", "11111", "Borked(Incompatible)"),
        ]
        assert result == expected
        assert mock_check_proton.call_count == 4

    @pytest.mark.parametrize(
        "tier_filter, api_returns, expected_output",
        [
            ("Bronze", "bronze", "Bronze"),
            ("Silver", "silver", "Silver"),
            ("Gold", "gold", "Gold"),
            ("Platinum", "platinum", "Platinum"),
        ])
    async def test_filter_specific_tiers(self, mock_check_proton, tier_filter, api_returns, expected_output, sample_games):
        games = sample_games
        
        mock_check_proton.side_effect = lambda appid: api_returns if appid == "67890" else "borked"

        result = await func.filter_games_by_tier(games, tier_filter)

        expected = [
            ("Game Two", "67890", expected_output),
        ]
        assert result == expected
        assert mock_check_proton.call_count == 4

    async def test_compatible_mode_filters_out_borked(self, mock_check_proton, sample_games):
        games = sample_games

        def side_effect(appid):
            if appid == "12345":
                return "borked"
            elif appid == "11111":
                return "borked"
            elif appid == "67890":
                return "gold"
            elif appid == "22222":
                return "native"
            else:
                return "unknown"
        mock_check_proton.side_effect = side_effect

        result = await func.filter_games_by_tier(games, "Compatible")

        expected = [("Game Two", "67890", "gold"), ("Game Four", "22222", "native")]
        assert result == expected
    async def test_rate_limiting_sleep_triggers_correctly(self, mock_check_proton, mock_sleep):
        games = {i: f"Game {i}" for i in range(1, 26)}
        mock_check_proton.return_value = "gold"

        await func.filter_games_by_tier(games, "Gold")

        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(1)
    async def test_empty_games_dict(self, mock_check_proton, mock_sleep):
        result = await func.filter_games_by_tier({}, "Gold")
        assert result == []
        mock_check_proton.assert_not_called()
        mock_sleep.assert_not_called()