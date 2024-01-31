from datetime import datetime
from typing import Any, Dict, List, Optional

from db import ActiveStats, DefensePassingStats, PassingRun, PassingStats, PlayerInfo, db
from peewee import ModelSelect, fn

NUM_GAMES: float = 17.0


class Dao:
    def save_prediction(
        self, name: str, opponent: str, is_home_game: bool, year: int, passing_yards: float
    ) -> None:
        PassingRun.create(
            name=name,
            opponent=opponent,
            is_home_game=is_home_game,
            year=year,
            passing_yards=passing_yards,
        )

    def get_prediction(self, name: str, opponent: str, is_home_game: bool, year: int) -> Optional[float]:
        query = (
            PassingRun.select()
            .where(PassingRun.name == name)
            .where(PassingRun.opponent == opponent)
            .where(PassingRun.is_home_game == is_home_game)
            .where(PassingRun.year == year)
        )
        return self.parse_passing_run(query)

    def parse_passing_run(self, query: ModelSelect) -> float | None:
        rows = [row for row in query]
        if not rows:
            return None
        assert len(rows) == 1
        return float(rows[0].passing_yards)

    # def get_predictions():

    def train_passing_yds(self) -> None:
        db.execute_sql(
            sql="""
                DROP TABLE IF EXISTS public.nfl_features;
                CREATE TABLE public.features AS SELECT * FROM public.nfl_features();
            """
        )

        with db.execute_sql(
            sql="""SELECT * FROM pgml.train(
                    project_name => 'nfl_passing_yards',
                    task => 'regression',
                    relation_name => 'features',
                    y_column_name => 'pass_yards',
                    algorithm => 'lightgbm'
                );"""
        ) as cursor:
            print(f"{cursor.fetchall()[0]}")

    def get_player_info(self, name: str, year: int) -> Dict[str, Any]:
        now = datetime.now().year
        diff = now - 1 - year
        query = PlayerInfo.select().where(PlayerInfo.name == name).limit(1)
        return {
            "name": query[0].name,
            "year": year,
            "age": int(query[0].age) - diff,
            "experience": int(query[0].experience) - diff,
        }

    def get_player_active_stats(self, name: str, year: int) -> Dict[str, Any]:
        return {
            "name": name,
            "year": year,
            "pass_attempts": float(
                ActiveStats.select(fn.AVG(ActiveStats.pass_attempts))
                .where(ActiveStats.name == name)
                .scalar()
            ),
            "pass_completions": float(
                ActiveStats.select(fn.AVG(ActiveStats.pass_completions))
                .where(ActiveStats.name == name)
                .scalar()
            ),
            "pass_avg": float(
                ActiveStats.select(fn.AVG(ActiveStats.pass_avg)).where(ActiveStats.name == name).scalar()
            ),
            "rating": float(
                PassingStats.select(PassingStats.rate)
                .where(PassingStats.player == name)
                .where(PassingStats.year == year)
                .limit(1)
                .scalar()
            ),
        }

    def get_defense_stats(self, team: str, year: int) -> Dict[str, Any]:
        return {
            "team": team,
            "year": year,
            "avg_pass_att_against": float(
                DefensePassingStats.select(DefensePassingStats.attempts)
                .where(DefensePassingStats.team == team)
                .where(DefensePassingStats.year == year)
                .scalar()
            )
            / NUM_GAMES,
            "avg_completions_against": float(
                DefensePassingStats.select(DefensePassingStats.completions)
                .where(DefensePassingStats.team == team)
                .where(DefensePassingStats.year == year)
                .scalar()
            )
            / NUM_GAMES,
            "avg_yds_att_against": float(
                DefensePassingStats.select(DefensePassingStats.yds_att)
                .where(DefensePassingStats.team == team)
                .where(DefensePassingStats.year == year)
                .scalar()
            ),
            "avg_sacks": float(
                DefensePassingStats.select(DefensePassingStats.sacks)
                .where(DefensePassingStats.team == team)
                .where(DefensePassingStats.year == year)
                .scalar()
            )
            / NUM_GAMES,
        }

    def get_player_names(self) -> List[str]:
        query = (
            PlayerInfo.select(PlayerInfo.name)
            .where(PlayerInfo.position == "QB")
            .where(PlayerInfo.active)
        )
        return [name.name for name in query]

    def get_team_names(self) -> List[str]:
        query = DefensePassingStats.select(DefensePassingStats.team).where(
            DefensePassingStats.year == datetime.now().year - 1
        )
        return [team.team for team in query]


if __name__ == "__main__":
    dao = Dao()
    print(dao.get_player_names())
    print(dao.get_team_names())
