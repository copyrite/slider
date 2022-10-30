import itertools
import sqlite3
from contextlib import suppress
from io import StringIO

import requests
from lxml import etree

APPID = 1478340


def get_tree(url):
    response = requests.get(url)
    html = response.content.decode("utf-8")
    return etree.parse(StringIO(html), parser=etree.HTMLParser())


if __name__ == "__main__":
    with sqlite3.connect("slider.db") as con:
        cur = con.cursor()
        with suppress(sqlite3.OperationalError):
            cur.execute("CREATE TABLE user(id PRIMARY KEY, handle)")

        with suppress(sqlite3.OperationalError):
            cur.execute(
                "CREATE TABLE lb(track, user, car, time, PRIMARY KEY(track, user, car))"
            )

        initial = f"https://steamcommunity.com/stats/{APPID}/leaderboards"
        tree = get_tree(initial)
        leaderboard_options = tree.xpath("//select[@id = 'lbID']/option")

        for board in leaderboard_options:
            track, _, car = board.text.strip().rpartition(" with ")
            print(board.text)
            # sr = "starting rank"
            for sr in itertools.count(1, 15):
                url = f"{initial}/{board.get('value')}/?sr={sr}"
                tree = get_tree(url)
                leaderboard_entries = tree.xpath(
                    "//div[@id = 'stats']/div[@class = 'lbentry']"
                )

                for entry in leaderboard_entries:
                    player_link = entry.xpath("div//a[@class = 'playerName']")[0]

                    player_id = (
                        player_link.get("href")
                        .partition("https://steamcommunity.com/profiles/")[2]
                        .rpartition(f"/stats/{APPID}")[0]
                    ) or (  # TODO: look up the actual profile id
                        player_link.get("href")
                        .partition("https://steamcommunity.com/id/")[2]
                        .rpartition(f"/stats/{APPID}")[0]
                    )
                    player_name = player_link.text
                    cur.execute(
                        "REPLACE INTO user VALUES(?, ?)", (player_id, player_name)
                    )

                    time = int(
                        "".join(
                            char
                            for char in entry.xpath("div[@class='score']")[0].text
                            if char in "1234567890"
                        )
                    )

                    cur.execute(
                        "REPLACE INTO lb VALUES(?, ?, ?, ?)",
                        (track, player_id, car, time),
                    )

                if (
                    leaderboard_entries[0].xpath("div/div[@class = 'rR']")[0].text
                    != f"#{sr}"
                ):
                    break
