import logging
from dataclasses import dataclass
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from db import DefensePassingStats


@dataclass
class TeamService:
    root_url: str

    def __init__(self, root_url: str) -> None:
        self.root_url = root_url

    def run_pass(self, start_yr: int, end_yr: int) -> None:
        to_create = list(self.fetch_passing(start_yr, end_yr))
        DefensePassingStats.bulk_create(to_create)

    def fetch_passing(self, start_yr: int, end_yr: int) -> Iterable[DefensePassingStats]:
        for year in range(start_yr, end_yr):
            stats = self.fetch_defense_stats("passing", year)
            for row in stats.values.tolist():
                yield DefensePassingStats(
                    team=row[0][: int(len(row[0]) / 2)],
                    year=year,
                    attempts=row[1],
                    completions=row[2],
                    completion_percentage=row[3],
                    yds_att=row[4],
                    yards=row[5],
                    touchdowns=row[6],
                    interceptions=row[7],
                    first_downs=row[8],
                    first_down_percentage=row[9],
                    sacks=row[10],
                )

    def fetch_defense_stats(self, category: str, year: int) -> pd.DataFrame:
        logging.info(f"Fetching NFL {year} Team Stats for category: {category}")
        url = self.root_url + "/stats/team-stats/defense/" + category + "/" + str(year) + "/reg/all"
        resp = requests.get(url)
        assert resp.ok, f"Request error: {resp.status_code!r} - {resp.content!r}"
        soup = BeautifulSoup(resp.text, features="html.parser")

        table = soup.find("table")
        df = pd.read_html(str(table))[0]
        df = df.fillna(0)
        return df


if __name__ == "__main__":
    TeamService("https://www.nfl.com").run_pass(2022, 2023)
