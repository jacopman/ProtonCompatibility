import os
import asyncio
from dotenv import load_dotenv

# system functionality including both main() and modeSelection()
import wrappers

# Loading the .env file and assigning the values to the variables
load_dotenv()
STEAM_API_KEY = os.getenv("SteamApiKey")
STEAM_ID = os.getenv("SteamId")


try:
    asyncio.run(wrappers.main(STEAM_API_KEY, STEAM_ID))
except SystemError as e:
    print(f"Error: {e}")