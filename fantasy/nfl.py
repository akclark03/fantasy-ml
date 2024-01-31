import logging
import sys
from dataclasses import dataclass

from player_info import PlayerService
from season_stats import SeasonStatsService
from team_stats import TeamService

logging.basicConfig(
    format="%(asctime)s %(levelname)-5s [%(name)-16s]  %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@dataclass
class NFLStatsEtl:
    season_stats: SeasonStatsService
    team_stats: TeamService
    root_url: str = "https://www.nfl.com"

    def __init__(self) -> None:
        self.season_stats = SeasonStatsService(self.root_url)
        self.player_info = PlayerService(self.root_url)
        self.team_stats = TeamService(self.root_url)

    def run(self, start_yr: int, end_yr: int) -> None:
        self.season_stats.run_pass(start_yr, end_yr)
        self.team_stats.run_pass(start_yr, end_yr)


if __name__ == "__main__":
    NFLStatsEtl().run(2015, 2023)
