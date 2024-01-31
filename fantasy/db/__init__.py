# type: ignore
from peewee import BooleanField, CharField, CompositeKey, FloatField, IntegerField, Model
from playhouse.db_url import connect, register_database
from playhouse.postgres_ext import PostgresqlExtDatabase

register_database(PostgresqlExtDatabase, "postgres", "postgresql")  # needed for JSON support
db = connect("postgres://user:pass@localhost:5432/db")


class BaseModel(Model):
    class Meta:
        database = db


class PlayerInfo(BaseModel):
    name = CharField()
    position = CharField()
    active = BooleanField()
    team = CharField(null=True)
    height = IntegerField(null=True)
    weight = IntegerField(null=True)
    arms = FloatField(null=True)
    hands = FloatField(null=True)
    experience = IntegerField(null=True)
    college = CharField(null=True)
    age = IntegerField(null=True)
    hometown = CharField(null=True)

    class Meta:
        table_name = "players"
        primary_key = CompositeKey("name", "position")


class ActiveStats(BaseModel):
    name = CharField()
    week = IntegerField()
    opponent = CharField()
    home = BooleanField()
    game_result = CharField()
    pass_completions = IntegerField()
    pass_attempts = IntegerField()
    pass_yards = IntegerField()
    pass_avg = FloatField()
    pass_touchdowns = IntegerField()
    interceptions = IntegerField()
    sacks = IntegerField()
    sack_yards = IntegerField()
    rating = FloatField()
    rush_attempts = IntegerField()
    rush_yards = IntegerField()
    rush_avg = IntegerField()
    rush_touchdowns = IntegerField()
    fumbles = IntegerField()
    fumbles_lost = IntegerField()

    class Meta:
        table_name = "active_stats"
        primary_key = CompositeKey("name", "week")


class DefensePassingStats(BaseModel):
    team = CharField()
    year = IntegerField()
    attempts = IntegerField()
    completions = IntegerField()
    completion_percentage = FloatField()
    yds_att = FloatField()
    yards = IntegerField()
    touchdowns = IntegerField()
    interceptions = IntegerField()
    first_downs = IntegerField()
    first_down_percentage = FloatField()
    sacks = IntegerField()

    class Meta:
        table_name = "defense_passing_stats"
        primary_key = CompositeKey("team", "year")


class PassingStats(BaseModel):
    year = IntegerField()
    player = CharField()
    pass_yds = IntegerField()
    yds_att = FloatField()
    att = IntegerField()
    cmp = IntegerField()
    cmp_pct = FloatField()
    td = IntegerField()
    int = IntegerField()
    rate = FloatField()
    first = IntegerField()
    first_pct = FloatField()
    twenty_plus = IntegerField()
    forty_plus = IntegerField()
    lng = IntegerField()
    sck = IntegerField()
    scky = IntegerField()

    class Meta:
        table_name = "passing_stats"
        primary_key = CompositeKey("year", "player")


class RushingStats(BaseModel):
    year = IntegerField()
    player = CharField()
    rush_yds = IntegerField()
    att = IntegerField()
    td = IntegerField()
    twenty_plus = IntegerField()
    forty_plus = IntegerField()
    lng = IntegerField()
    rush_first = IntegerField()
    rush_first_pct = FloatField()
    rush_fum = IntegerField()

    class Meta:
        table_name = "rushing_stats"
        primary_key = CompositeKey("year", "player")


class ReceivingStats(BaseModel):
    year = IntegerField()
    player = CharField()
    rec = IntegerField()
    yds = IntegerField()
    td = IntegerField()
    twenty_plus = IntegerField()
    forty_plus = IntegerField()
    lng = IntegerField()
    rec_first = IntegerField()
    first_pct = FloatField()
    rec_fum = IntegerField()
    rec_yac_r = IntegerField()
    tgts = IntegerField()

    class Meta:
        table_name = "receiving_stats"
        primary_key = CompositeKey("year", "player")


class FieldGoalStats(BaseModel):
    year = IntegerField()
    player = CharField()
    fgm = IntegerField()
    att = IntegerField()
    fg_pct = FloatField()
    one_nineteen_a_m = CharField()
    twenty_twentynine_a_m = CharField()
    thirty_thirtynine_a_m = CharField()
    forty_fortynine_a_m = CharField()
    fifty_fiftynine_a_m = CharField()
    sixty_plus_a_m = CharField()
    lng = IntegerField()
    fg_blk = IntegerField()

    class Meta:
        table_name = "field_goal_stats"
        primary_key = CompositeKey("year", "player")


class PassingRun(BaseModel):
    name = CharField()
    opponent = CharField()
    is_home_game = CharField()
    year = IntegerField()
    passing_yards = FloatField()

    class Meta:
        table_name = "passing_run"
        primary_key = CompositeKey("name", "opponent")
