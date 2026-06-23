import subprocess
import asyncio
import os

import func

def print_compatibility_report(filtered_games: list[tuple[str, str, str]], mode: str) -> None:
    """
    Prints to the console a formatted report of all the games according to the specified filter.

    Parameters:
        games (list [tuple[str, str, str]]): The list of games to report including their AppID and compatibility tier.
        mode (str): The tier filter requirement.
    Returns:
        None
    """
    print("\n" + "=="*40)
    print(f"{mode.upper()} GAMES LIST")
    print("=="*40)
    if filtered_games:
        if mode == "compatible":
            for i, (name, appId, tier) in enumerate(filtered_games, 1):
                print(f"{i} - {name} (AppID: {appId}): - Compatibility: {tier}")
        elif mode == "incompatible":
            for i, (name, appId, _) in enumerate(filtered_games, 1):
                print(f"{i} - {name} (AppID: {appId})")
        else:
            for i, (name, appId, _) in enumerate(filtered_games, 1):
                print(f"{i} - {name} (AppID: {appId})")
    else:
        if mode == "incompatible":
            print("All your games are compatible with ProtonDB or unrated/native!")
        elif mode == "compatible":
            print("All your games are compatible with ProtonDB!")
        else:
            print(f"No {mode} tier games found in your library.")

    # if filtered_games and mode == "compatible":
    #     for name, appid, tier in filtered_games:
    #         print(f"{name} (AppID: {appid}) - Compatibility: {tier}")
    # elif filtered_games:
    #     for name, appid, tier in filtered_games:
    #         print(f"{name} (AppID: {appid})")
    # else:
    #     if mode == "incompatible":
    #         print("All your games are compatible with ProtonDB or unrated/native!")
    #     elif mode == "compatible":
    #         print("All your games are compatible with ProtonDB!")
    #     else:
    #         print(f"No {mode} tier games found in your library.")

def modeSelection() -> str:
    """
    Tier filter selection Tool.

    Parameters:
        None: 
    Returns:
        str: The selected tier, Preformatted for normalized string responses
    """
    searchType = ["Incompatible", "Bronze", "Silver", "Gold", "Platinum", "Compatible"]
    selected = False
    selectedOption = 0
    prompt = "Select a compatibility tier to search for (⌃ + ⌄ to navigate, Enter to select):"
    while not selected:
        subprocess.run(['cls'] if os.name == 'nt' else ['clear'], shell=True)
        print()
        print(prompt)
        for i, option in enumerate(searchType):
            if (i == selectedOption):
                print(f"\033[31m{i+1}. {option}\033[0m")
            else:
                print(f"{i+1}. {option}")
        key = func.get_keystroke()

        if (key == '\x1b[A'):
            selectedOption = (selectedOption - 1) % len(searchType)
            prompt = "Select a compatibility tier to search for (⌃ + ⌄ to navigate, Enter to select):"

        elif (key == '\x1b[B'):
            selectedOption = (selectedOption + 1) % len(searchType)
            prompt = "Select a compatibility tier to search for (⌃ + ⌄ to navigate, Enter to select):"
        elif (key == '\r'):
            selected = True
        else:
            prompt = "Invalid input. Please use the arrow keys to navigate and Enter to select"
        # selectedOption = int(input("Enter your choice: ")) - 1
        # if 0 <= selectedOption < len(searchType):
        #     selected = True
    return searchType[selectedOption]

async def main(apiKey: str | None, steamId: str| None):
    """
    Main function to run the compatibility check.
    ## Warning:
        if either `apiKey` or `steamId` is None:
            the function end with no action.

    Arguments:
        mode (str): The selected compatibility tier (should be normalized via `modeSelection()`).
        apiKey (str | None): The Steam API key.
        steamId (str| None): The Steam ID of the user.
    Returns:
        None:
    """
    if (apiKey is None or steamId is None):
        raise SystemError("Either `apiKey` or `steamId` is None.")
    mode = modeSelection()
    library = func.get_steam_library(apiKey, steamId)
    if not library:
        raise SystemError("no library found")

    async with asyncio.TaskGroup() as tg:
        print(f"Found {len(library)} games in the library.")
        task1 = tg.create_task(func.filter_games_by_tier(library, mode))
        print(f"Filtering games by {mode.capitalize()} tier...", end="")

    filteredLibrary = task1.result()
    print(f"Found {len(filteredLibrary)} matching games.\n")
    print_compatibility_report(filteredLibrary, mode=mode)