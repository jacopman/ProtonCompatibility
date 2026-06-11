import os

from dotenv import load_dotenv
import pytest
import wrappers
import asyncio


class testDotEnv:
    def empty_env_throws_error(self, monkeypatch):
        monkeypatch.delenv("SteamApiKey", "")
        monkeypatch.delenv("SteamID", "")
        with pytest.raises(SystemError):
            load_dotenv()
            STEAM_API_KEY = os.getenv("SteamApiKey")
            STEAM_ID = os.getenv("SteamID")
            asyncio.run(wrappers.main(STEAM_API_KEY, STEAM_ID))