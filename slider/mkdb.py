import os
import sqlite3
from contextlib import suppress

import dotenv
import requests
import steamleaderboards
from more_itertools import chunked

APPID = 1478340

BUILTIN_CARS = {
    "Sporty",
    "Drifty",
    "Grippy",
}

BUILTIN_TRACKS = {
    "Tutoring",
    "Leapyloop",
    "Hilcutti",
    "Winderun",
    "Seabreach",
    "Greendewald",
    "Treypecs",
    "Britzbane",
    "Springshire",
    "Sandyfalls",
    "Brickrise",
    "Twisted Ascension",
    "Luckdewald",
}

SILLY_TRACKS = {
    "Sandyfalls",
    "Brickrise",
    "Twisted Ascension",
    "Luckdewald",
}


if __name__ == "__main__":
    dotenv.load_dotenv()

    with sqlite3.connect("slider.db") as con:
        cur = con.cursor()
        with suppress(sqlite3.OperationalError):
            cur.execute("CREATE TABLE user(id PRIMARY KEY, handle)")

        with suppress(sqlite3.OperationalError):
            cur.execute("CREATE TABLE track(name PRIMARY KEY, is_builtin, is_silly)")

        with suppress(sqlite3.OperationalError):
            cur.execute(
                "CREATE TABLE lb(track, user, car, time, PRIMARY KEY(track, user, car))"
            )

        users = set()

        lbgroup = steamleaderboards.LeaderboardGroup(APPID)
        for lb in lbgroup.leaderboards:
            track, _, car = lb.display_name.strip().rpartition(" with ")

            # Skip over badly parsing leaderboards
            if not track or track not in BUILTIN_TRACKS or car not in BUILTIN_CARS:
                continue

            print(track, car)

            cur.execute(
                "REPLACE INTO track VALUES(?, ?, ?)",
                (track, track in BUILTIN_TRACKS, track in SILLY_TRACKS),
            )

            for entry in lb.full().entries:
                users |= {entry.steam_id}

                cur.execute(
                    "REPLACE INTO lb VALUES(?, ?, ?, ?)",
                    (track, entry.steam_id, car, entry.score),
                )

        # Get usernames
        for batch in chunked(users, 100):
            response = requests.get(
                f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/",
                params={
                    "key": os.getenv("STEAM_WEB_API_KEY", 0),
                    "steamids": ",".join(batch),
                },
            )
            for entry in response.json()["response"]["players"]:
                cur.execute(
                    "REPLACE INTO user VALUES(?, ?)",
                    (entry["steamid"], entry["personaname"]),
                )
