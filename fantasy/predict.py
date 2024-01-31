from datetime import datetime
from typing import List, Optional

from daos import Dao
from db import db
from peewee import IntegrityError


class PassingPredictor:
    def __init__(self, dao: Dao) -> None:
        self.dao = dao

    def predict(
        self,
        name: str,
        opponent: str,
        is_home_game: bool,
        year: int,
    ) -> float:
        player_info = self.dao.get_player_info(name, year)
        active_stats = self.dao.get_player_active_stats(name, year)
        defense_stats = self.dao.get_defense_stats(opponent, year)

        with db.execute_sql(
            sql="""SELECT pgml.predict(
                    'nfl_passing_yards'::TEXT,
                    ARRAY[
                        %s::INT4,      -- Age
                        %s::INT4,      -- Experience
                        %s::FLOAT4,    -- Avg Pass Attempts
                        %s::FLOAT4,    -- Avg Pass Completions
                        %s::FLOAT4,    -- Avg Yards per Attempt
                        %s::FLOAT4,    -- Ovr Passer Rating
                        %s::INT4,      -- Is Home
                        %s::INT4,      -- IS Away
                        %s::FLOAT4,    -- Defense Average Pass Attempts Against
                        %s::FLOAT4,    -- Defense Average Completions Against
                        %s::FLOAT4,    -- Defense Average Yards per Attempts Against
                        %s::FLOAT4     -- Defense Average Sacks
                    ]
                ) AS prediction;""",
            params=[
                player_info["age"],
                player_info["experience"],
                active_stats["pass_attempts"],
                active_stats["pass_completions"],
                active_stats["pass_avg"],
                active_stats["rating"],
                1 if is_home_game else 0,
                0 if is_home_game else 1,
                defense_stats["avg_pass_att_against"],
                defense_stats["avg_completions_against"],
                defense_stats["avg_yds_att_against"],
                defense_stats["avg_sacks"],
            ],
        ) as cursor:
            return float(cursor.fetchall()[0][0])

    def run(  # type: ignore
        self,
        persist: Optional[bool] = True,
    ):
        names = self.dao.get_player_names()
        teams = self.dao.get_team_names()
        year = datetime.now().year - 1

        self.prediction_run(persist, names, teams, True, year)  # type: ignore
        self.prediction_run(persist, names, teams, False, year)  # type: ignore

    def prediction_run(
        self, persist: bool, names: List[str], teams: List[str], is_home_game: bool, year: int
    ) -> None:
        for name in names:
            for opponent in teams:
                existing = self.dao.get_prediction(name, opponent, is_home_game, year)
                if persist and existing:
                    continue

                prediction = self.predict(name, opponent, is_home_game, year)

                if persist:
                    try:
                        self.dao.save_prediction(name, opponent, is_home_game, year, prediction)
                    except IntegrityError as err:
                        print(err)
