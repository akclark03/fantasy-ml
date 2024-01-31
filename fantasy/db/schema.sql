--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: Andrew Clark
--

-- *not* creating schema, since initdb creates it

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: players; Type: TABLE; Schema: public;
--

CREATE TABLE public.players (
    "name" varchar NOT NULL,
    position varchar NOT NULL,
    active boolean,
    team varchar,
    height integer,
    "weight" integer,
    arms float,
    hands float,
    experience integer,
    college varchar,
    age integer,
    hometown varchar
);

--
-- Name: active_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.active_stats (
    name varchar NOT NULL,
    week integer NOT NULL,
    opponent varchar,
    home boolean,
    game_result varchar,
    pass_completions integer,
    pass_attempts integer,
    pass_yards integer,
    pass_avg float,
    pass_touchdowns integer,
    interceptions integer,
    sacks integer,
    sack_yards integer,
    rating float,
    rush_attempts integer,
    rush_yards integer,
    rush_avg integer,
    rush_touchdowns integer,
    fumbles integer,
    fumbles_lost integer
);

--
-- Name: defense_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.defense_passing_stats (
    team varchar NOT NULL,
    year integer NOT NULL,
    attempts integer,
    completions integer,
    completion_percentage float,
    yds_att float,
    yards integer,
    touchdowns integer,
    interceptions integer,
    first_downs integer,
    first_down_percentage float,
    sacks integer
);

--
-- Name: passing_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.passing_stats (
    "year" integer NOT NULL,
    player varchar NOT NULL,
    pass_yds integer,
    yds_att float,
    att integer,
    cmp integer,
    cmp_pct float,
    td integer,
    "int" integer,
    rate float,
    "first" integer,
    first_pct float,
    twenty_plus integer,
    forty_plus integer,
    lng integer,
    sck integer,
    scky integer
);

--
-- Name: rushing_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.rushing_stats (
    "year" integer NOT NULL,
    player varchar NOT NULL,
    rush_yds integer,
    att integer,
    td integer,
    twenty_plus integer,
    forty_plus integer,
    lng integer,
    rush_first integer,
    rush_first_pct float,
    rush_fum integer
);

--
-- Name: receiving_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.receiving_stats (
    "year" integer NOT NULL,
    player varchar NOT NULL,
    rec integer,
    yds integer,
    td integer,
    twenty_plus integer,
    forty_plus integer,
    lng integer,
    rec_first integer,
    first_pct float,
    rec_fum integer,
    rec_yac_r integer,
    tgts integer
);

--
-- Name: field_goal_stats; Type: TABLE; Schema: public;
--

CREATE TABLE public.field_goal_stats (
    "year" integer NOT NULL,
    player varchar NOT NULL,
    fgm integer,
    att integer,
    fg_pct float,
    one_nineteen_a_m varchar,
    twenty_twentynine_a_m varchar,
    thirty_thirtynine_a_m varchar,
    forty_fortynine_a_m varchar,
    fifty_fiftynine_a_m varchar,
    sixty_plus_a_m varchar,
    lng integer,
    fg_blk integer
);

--
-- Name: runs; Type: TABLE; Schema: public;
--

CREATE TABLE public.passing_run (
    name varchar NOT NULL,
    opponent varchar NOT NULL,
    is_home_game boolean NOT NULL,
    year integer NOT NULL,
    passing_yards float NOT NULL
);

CREATE FUNCTION public.nfl_features()
RETURNS TABLE(
    age INT4,
    experience INT4,
    pass_attempts FLOAT4,
    pass_completions FLOAT4,
    pass_yards FLOAT4,
    pass_avg FLOAT4,
    rating FLOAT4,
    is_home INT4,
    is_away INT4,
    def_avg_pass_att FLOAT4,
    dev_avg_completions FLOAT4,
    def_yds_att FLOAT4,
    def_avg_sacks FLOAT4
)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
	RETURN QUERY
    WITH stats AS (
        SELECT
            name,
            opponent,
            home,
            "as".pass_completions,
            "as".pass_attempts,
            "as".pass_yards,
            "as".pass_avg,
            "as".rating
        FROM active_stats "as"
        WHERE "as".pass_attempts > 0
    ), info AS (
        SELECT
            p.name,
            p.experience,
            p.age
        FROM players p
        WHERE NOT (
            p.name IS NULL OR p.experience IS NULL OR p.age IS NULL
        )
        AND "position" = 'QB'
    ), defense AS (
        SELECT
            team AS opponent,
            attempts::float / 17::float AS def_avg_pass_att,
            completions::float / 17::float AS def_avg_completions,
            yds_att AS def_yds_att,
            sacks::float / 17::float AS def_avg_sacks
        FROM defense_passing_stats
        WHERE "year" = (date_part('year', CURRENT_DATE) - 1)
    )
    SELECT
        i.age::INT4,
        i.experience::INT4,
        s.pass_attempts::FLOAT4,
        s.pass_completions::FLOAT4,
        s.pass_yards::FLOAT4,
        s.pass_avg::FLOAT4,
        s.rating::FLOAT4,
        CASE WHEN s.home IS TRUE THEN 1 ELSE 0 END AS is_home,
        CASE WHEN s.home IS TRUE THEN 0 ELSE 1 END AS is_away,
        d.def_avg_pass_att::FLOAT4,
        d.def_avg_completions::FLOAT4,
        d.def_yds_att::FLOAT4,
        d.def_avg_sacks::FLOAT4
    FROM stats s
    JOIN info i USING ("name")
    JOIN defense d USING ("opponent");
END
$$;

--
-- PostgreSQL database dump complete
--