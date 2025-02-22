#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER balancing_user WITH PASSWORD 'guitar123';
    CREATE DATABASE balancing_db;
    GRANT ALL PRIVILEGES ON DATABASE balancing_db TO balancing_user;
EOSQL