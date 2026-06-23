import requests as r

# Keystroke functionality
import sys
import termios
import tty
import asyncio


def get_keystroke() -> str:
    """
    keystroke Identification
    Parameters:
        None
    Returns:
        str: The keystroke character .
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        
        # If the character is an ESC code, check if it's an arrow key sequence
        if ch == '\x1b':
            # Read the next two characters ('[' and the direction indicator)
            ch += sys.stdin.read(2)
            
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def get_steam_library(api_key: str | None, steam_id: str | None, base_url: str = "http://api.steampowered.com") -> dict:
    """Fetches the user's Steam library.
    ## Warning: 
        If either `api_key` or `steam_id` is None, the function will return `{}`.
    Parameters:
        api_key (str | None): The Steam API key.
        steam_id (str | None): The Steam ID of the user.

    Returns:
        dict: A dictionary of {appid: game_name} for the user's library.


    """
    if not api_key or not steam_id:
        return {}
    url = f"{base_url}IplayerService/GetOwnedGames/v0001/"
    params = {
        'key': api_key,
        'steamid': steam_id,
        'include_appinfo': True,
        'include_played_free_games': True
    }
    try:
        response = r.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        games = data.get('response', {}).get('games', [])
        if not games:
            return {}
        return {game['appid']: game['name'] for game in games}
    except r.exceptions.RequestException as e:
        print(f"Error fetching Steam library: {e}")
        return {}

async def check_proton_compatibility(appid: str) -> str:
    """queries ProtonDB for a game's compatibility tier rating
    Parameters:
        appid (str): The app ID of the game to check.

    Returns:
        str: The tier string (e.g., 'borked', 'gold') or None if not rated/native."""
    url = f"https://www.protondb.com/api/v1/reports/summaries/{appid}.json"
    try:
        response = r.get(url, timeout=10)
        if (response.status_code == 404):
            #404 usually means a game is either completely unrated or runs natively on Linux
            return "unknown/native"
        response.raise_for_status()

        #ProtonDB returns data in a format containing a 'tier' key
        data = response.json()
        return data.get("tier", "unknown")
    except r.exceptions.RequestException as e:
        print(f"Error fetching ProtonDB data for appid {appid}: {e}")
        return "error"

async def filter_games_by_tier(games: dict, tierFilter: str) -> list[tuple[str, str, str]]:
    """
    Filters a game library by a specified tier.

    Parameters:
        games ( dict { appid: game_name } ): The dictionary of games to filter.
        tierFilter (str): The tier to filter by.

    Returns:
        tuple(str name, str appid, str tier): only games of the sepecified tier
    """
    filtered_games = []
    for i, (appid, name) in enumerate(games.items(), 1):
        tier = await check_proton_compatibility(appid)
        if tierFilter == "Incompatible":
            if (tier == "borked"):
                filtered_games.append((name, appid, "Borked(Incompatible)"))
            else:
                pass
        elif tierFilter == "Bronze":
            if (tier == "bronze"):
                filtered_games.append((name, appid, "Bronze"))
            else:
                pass
        elif tierFilter == "Silver":
            if (tier == "silver"):
                filtered_games.append((name, appid, "Silver"))
            else:
                pass
        elif tierFilter == "Gold":
            if (tier == "gold"):
                filtered_games.append((name, appid, "Gold"))
            else:
                pass
        elif tierFilter == "Platinum":
            if (tier == "platinum"):
                filtered_games.append((name, appid, "Platinum"))
            else:
                pass
        # compatible mode
        else:
            if (tier == "borked"):
                pass
            else:
                filtered_games.append((name, appid, tier))

        # To respect ProtonDB's servers, we introduce a tiny delay between requests
        if i % 10 == 0 :
            await asyncio.sleep(1)
    return filtered_games

if __name__ == "__main__":
    
    library = get_steam_library("AE82776728C5D740C678BCD64C5F7115", "76561198871950343")
    for (_, game_ID) in enumerate(library):
        print(f"{library[game_ID]} (AppID: {game_ID})")