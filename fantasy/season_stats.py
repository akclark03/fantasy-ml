import logging
from dataclasses import dataclass
from typing import Dict, Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from db import FieldGoalStats, PassingStats, ReceivingStats, RushingStats
from player_info import PlayerService


@dataclass
class SeasonStatsService:
    root_url: str
    player_service: PlayerService

    def __init__(self, root_url: str) -> None:
        self.root_url = root_url
        self.player_service = PlayerService(root_url)
        self.categories: Dict[str, str] = {
            "passing": "passingyards",
            "rushing": "rushingyards",
            "receiving": "receivingreceptions",
            "fumbles": "defensiveforcedfumble",
            "tackles": "defensivecombinetackles",
            "interceptions": "defensiveinterceptions",
            "field-goals": "kickingfgmade",
            "kickoffs": "kickofftotal",
            "kickoff-returns": "kickreturnsaverageyards",
            "punts": "puntingaverageyards",
            "punt-returns": "puntreturnsaverageyards",
        }

    def run_pass(self, start_yr: int, end_yr: int) -> None:
        to_create = list(self.fetch_passing(start_yr, end_yr))
        PassingStats.bulk_create(to_create)

    def run_rush(self, start_yr: int, end_yr: int) -> None:
        to_create = list(self.fetch_rushing(start_yr, end_yr))
        RushingStats.bulk_create(to_create)

    def run_rec(self, start_yr: int, end_yr: int) -> None:
        to_create = list(self.fetch_receiving(start_yr, end_yr))
        ReceivingStats.bulk_create(to_create)

    def run_fg(self, start_yr: int, end_yr: int) -> None:
        to_create = list(self.fetch_field_goal_stats(start_yr, end_yr))
        FieldGoalStats.bulk_create(to_create)

    def fetch_passing(self, start_yr: int, end_yr: int) -> Iterable[PassingStats]:
        for year in range(start_yr, end_yr):
            stats = self.fetch_player_stats("passing", year)
            for row in stats.values.tolist():
                yield PassingStats(
                    year=year,
                    player=row[0],
                    pass_yds=row[1],
                    yds_att=row[2],
                    att=row[3],
                    cmp=row[4],
                    cmp_pct=row[5],
                    td=row[6],
                    int=row[7],
                    rate=row[8],
                    first=row[9],
                    first_pct=row[10],
                    twenty_plus=row[11],
                    forty_plus=row[12],
                    lng=row[13],
                    sck=row[14],
                    scky=row[15],
                )

    def fetch_rushing(self, start_yr: int, end_yr: int) -> Iterable[RushingStats]:
        for year in range(start_yr, end_yr):
            stats = self.fetch_player_stats("rushing", year)
            for row in stats.values.tolist():
                yield RushingStats(
                    year=year,
                    player=row[0],
                    rush_yds=row[1],
                    att=row[2],
                    td=row[3],
                    twenty_plus=row[4],
                    forty_plus=row[5],
                    lng=row[6],
                    rush_first=row[7],
                    rush_first_pct=row[8],
                    rush_fum=row[9],
                )

    def fetch_receiving(self, start_yr: int, end_yr: int) -> Iterable[ReceivingStats]:
        for year in range(start_yr, end_yr):
            stats = self.fetch_player_stats("receiving", year)
            for row in stats.values.tolist():
                yield ReceivingStats(
                    year=year,
                    player=row[0],
                    rec=row[1],
                    yds=row[2],
                    td=row[3],
                    twenty_plus=row[4],
                    forty_plus=row[5],
                    lng=row[6],
                    rec_first=row[7],
                    first_pct=row[8],
                    rec_fum=row[9],
                    rec_yac_r=row[10],
                    tgts=row[11],
                )

    def fetch_field_goal_stats(self, start_yr: int, end_yr: int) -> Iterable[FieldGoalStats]:
        for year in range(start_yr, end_yr):
            stats = self.fetch_player_stats("field-goals", year)
            for row in stats.values.tolist():
                yield FieldGoalStats(
                    year=year,
                    player=row[0],
                    fgm=row[1],
                    att=row[2],
                    fg_pct=row[3],
                    one_nineteen_a_m=row[4],
                    twenty_twentynine_a_m=row[5],
                    thirty_thirtynine_a_m=row[6],
                    forty_fortynine_a_m=row[7],
                    fifty_fiftynine_a_m=row[8],
                    sixty_plus_a_m=row[9],
                    lng=row[10],
                    fg_blk=row[11],
                )

    def fetch_player_stats(self, category: str, year: int) -> pd.DataFrame:
        logging.info(f"Fetching NFL {year} Player Stats for category: {category}")
        url = (
            self.root_url
            + "/stats/player-stats/category/"
            + category
            + "/"
            + str(year)
            + "/reg/all/"
            + self.categories[category]
            + "/desc"
        )
        resp = requests.get(url)
        assert resp.ok, f"Request error: {resp.status_code!r} - {resp.content!r}"
        soup = BeautifulSoup(resp.text, features="html.parser")

        table = soup.find("table")

        player_rows = table.find_all("a", href=True, class_="d3-o-player-fullname nfl-o-cta--link")
        self.player_service.run([player["href"] for player in player_rows])

        df = pd.read_html(str(table))[0]
        next = soup.find("a", href=True, class_="nfl-o-table-pagination__next")
        while next is not None:
            url = self.root_url + next["href"]
            resp = requests.get(url)
            assert resp.ok, f"Request error: {resp.status_code!r} - {resp.content!r}"
            soup = BeautifulSoup(resp.text, features="html.parser")

            table = soup.find("table")

            player_rows = table.find_all("a", href=True, class_="d3-o-player-fullname nfl-o-cta--link")
            self.player_service.run([player["href"] for player in player_rows])

            df = pd.concat([df, pd.read_html(str(table))[0]], ignore_index=True)
            next = soup.find("a", href=True, class_="nfl-o-table-pagination__next")

        return df[df["Player"].notna()]
