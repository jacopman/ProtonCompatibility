import requests as r
import time as t

STEAM_API_KEY = ""

# instert your steam id here, you can find it by going to your steam profile and copying the long number at the end of the url, 
# or by using a steam id finder tool online. It should be a 17 digit number.

STEAM_ID = "THIS NEEDS TO BE REPLACED WITH YOUR OWN ACCOUNT ID"

def get_steam_library(api_key: str, steam_id: str) -> dict:
    """Fetches a dict of {appid: game_name} from the user's Steam library."""
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
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
            print("No games found in the library.")
            return {}
        return {game['appid']: game['name'] for game in games}
    except r.exceptions.RequestException as e:
        print(f"Error fetching Steam library: {e}")
        return {}
def check_proton_compatibility(appid: str) -> str:
    """queries ProtonDB for a game's compatibility tier rating
    returns the tier string (e.g., 'borked', 'gold') or None if not rated/native."""
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

def print_compatibility_report(games: list, mode: str = "incompatible"):
    print("\n" + "=="*40)
    print(f"COMPATIBILITY: {mode.upper()} GAMES LIST")
    print("\n" + "=="*40)

    if games and mode == "compatible":
        for name, appid, tier in games:
            print(f"{name} (AppID: {appid}) - Compatibility: {tier}")
    elif games:
        for name, appid, _ in games:
            print(f"{name} (AppID: {appid})")
    else:
        if mode == "incompatible":
            print("All your games are compatible with ProtonDB or unrated/native!")
        elif mode == "compatible":
            print("All your games are compatible with ProtonDB!")
        else:
            print(f"No {mode} tier games found in your library.")
def main(mode: str = "incompatible"):
    print("Fetching your steam library...")
    library = get_steam_library(STEAM_API_KEY, STEAM_ID)
    if not library:
        return
    print(f"Found {len(library)} games in your library.\nchecking ProtonDB for compatibility...")

    games = []
    for i, (appid, name) in enumerate(library.items(), 1):
        tier = check_proton_compatibility(appid)
        #ProtonDB tiers: borked means complete incompatibiility, platinum means out of the box compatibility.
        if mode == "incompatible":
            if (tier == "borked"):
                games.append((name, appid, "Borked(Incompatible)"))
            else:
                pass
        elif mode == "bronze":
            if (tier == "bronze"):
                games.append((name, appid, "Bronze"))
            else:
                pass
        elif mode == "silver":
            if (tier == "silver"):
                games.append((name, appid, "Silver"))
            else:
                pass
        elif mode == "gold":
            if (tier == "gold"):
                games.append((name, appid, "Gold"))
            else:
                pass
        elif mode == "platinum":
            if (tier == "platinum"):
                games.append((name, appid, "Platinum"))
            else:
                pass

        # compatible mode
        else:
            games.append((name, appid, tier))

        # To respect ProtonDB's servers, we introduce a tiny delay between requests
        if i % 10 == 0 :
            t.sleep(1)

    print_compatibility_report(games, mode=mode)
    
    
if __name__ == "__main__":
    main()