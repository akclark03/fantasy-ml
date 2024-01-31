# nfl-stats

This repo  web scraps stats from the nfl website.

## Setup

1. Install deps

   ```bash
   brew install poetry
   poetry install
   ```

1. Deploy a database via [PostgresML's Quick Start w/ Docker](https://postgresml.org/docs/guides/setup/quick_start_with_docker)

   ```bash
   git clone https://github.com/postgresml/postgresml
   cd postgresml && docker-compose up -d
   ```

1. Load the schema

   ```bash
   psql -U postgres -h 127.0.0.1 -p 5433 pgml_development -f foxhole/db/schema.sql
   ```

By default, the postgres service will be exposed to postgresql://postgres@localhost:5433/pgml_development