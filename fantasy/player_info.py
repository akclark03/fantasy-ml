import logging
from dataclasses import dataclass
from typing import Iterable, List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from db import ActiveStats, PlayerInfo


@dataclass
class PlayerService:
    root_url: str

    def run(self, player_urls: List[str]) -> None:
        to_create = list(self.fetch_players(player_urls))
        PlayerInfo.bulk_create(to_create)

    def fetch_players(self, player_urls: List[str]) -> Iterable[PlayerInfo]:
        for player in player_urls:
            info = self.fetch_player_info(player)
            if info is not None:
                yield info

    def fetch_player_info(self, player_url: str) -> PlayerInfo:
        player = player_url.split("/")[2]
        logging.info(f"Fetching NFL Player info for: {player}")
        url = self.root_url + player_url
        resp = requests.get(url)
        assert resp.ok, f"Request error: {resp.status_code!r} - {resp.content!r}"
        soup = BeautifulSoup(resp.text, features="html.parser")

        name = soup.find("h1", class_="nfl-c-player-header__title").text
        if not PlayerInfo.select().where(PlayerInfo.name == name).exists():
            position = soup.find("span", class_="nfl-c-player-header__position").text.replace(" ", "")

            active = soup.find(
                "h3",
                class_="nfl-c-player-header__roster-status "
                + "nfl-c-player-header__roster-status--act nfl-u-hide-empty",
            )

            physical_data = {
                val.find("div", class_="nfl-c-player-info__key")
                .text: val.find("div", class_="nfl-c-player-info__value")
                .text
                for val in soup.find("ul", class_="d3-o-list nfl-c-player-info__physical-data").find_all(
                    "li", class_="d3-o-list__item"
                )
            }

            career_data = {
                val.find("div", class_="nfl-c-player-info__key")
                .text: val.find("div", class_="nfl-c-player-info__value")
                .text
                for val in soup.find("ul", class_="d3-o-list nfl-c-player-info__career-data").find_all(
                    "li", class_="d3-o-list__item"
                )
            }

            height = None
            if "Height" in physical_data and physical_data["Height"] != "":
                height = physical_data["Height"].split("-")
                height = int(height[0]) * 12 + int(height[1])

            weight = None
            if "Weight" in physical_data and physical_data["Weight"] != "":
                weight = int(physical_data["Weight"])

            arms = None
            if "Arms" in physical_data and physical_data["Arms"] != "":
                arms = physical_data["Arms"].split(" ")
                if len(arms) > 1:
                    arms = float(arms[0]) + float(arms[1].split("/")[0]) / float(arms[1].split("/")[1])
                else:
                    arms = float(arms[0])

            hands = None
            if "Hands" in physical_data and physical_data["Hands"] != "":
                hands = physical_data["Arms"].split(" ")
                if len(hands) > 1:
                    hands = float(hands[0]) + float(hands[1].split("/")[0]) / float(
                        hands[1].split("/")[1]
                    )
                else:
                    hands = float(hands[0])

            experience = None
            if "Experience" in career_data and career_data["Experience"] != "":
                experience = int(career_data["Experience"])

            college = None
            if "College" in career_data and career_data["College"] != "":
                college = career_data["College"]

            hometown = None
            if "Hometown" in career_data and career_data["Hometown"] != "":
                hometown = career_data["Hometown"]

            age = None
            if "Age" in career_data and career_data["Age"] != "":
                age = int(career_data["Age"])

            team = None

            if active is not None and active.text == "active":
                active = True

                if position == "QB":
                    to_create = self.fetch_active_stats(name, player_url)
                    ActiveStats.bulk_create(to_create)

                team = (
                    soup.find("div", class_="nfl-c-player-header__team nfl-u-hide-empty")
                    .find("a", class_="nfl-o-cta--link")
                    .text
                )
            else:
                active = False

            return PlayerInfo(
                name=name,
                position=position,
                active=active,
                team=team,
                height=height,
                weight=weight,
                arms=arms,
                hands=hands,
                experience=experience,
                college=college,
                age=age,
                hometown=hometown,
            )

    def fetch_active_stats(self, player_name: str, player_url: str) -> Iterable[ActiveStats]:
        player = player_url.split("/")[2]
        logging.info(f"Fetching NFL Player Recent Game Stats for: {player}")
        url = self.root_url + player_url + "/stats/"
        resp = requests.get(url)
        assert resp.ok, f"Request error: {resp.status_code!r} - {resp.content!r}"
        soup = BeautifulSoup(resp.text, features="html.parser")

        table = soup.find("table")
        if table is not None:
            df = pd.read_html(str(table))[0]
            df = df.fillna(0)
            for row in df.values.tolist():
                yield ActiveStats(
                    name=player_name,
                    week=row[0],
                    opponent=row[1].replace("@", ""),
                    home=False if row[1].__contains__("@") else True,
                    game_result=row[2].split(" ")[0],
                    pass_completions=row[3],
                    pass_attempts=row[4],
                    pass_yards=row[5],
                    pass_avg=row[6],
                    pass_touchdowns=row[7],
                    interceptions=row[8],
                    sacks=row[9],
                    sack_yards=row[10],
                    rating=row[11],
                    rush_attempts=row[12],
                    rush_yards=row[13],
                    rush_avg=row[14],
                    rush_touchdowns=row[15],
                    fumbles=row[16],
                    fumbles_lost=row[17],
                )


if __name__ == "__main__":
    service = PlayerService("https://www.nfl.com")
    service.fetch_player_info("/players/patrick-mahomes")
