#!/usr/bin/env python

import psycopg2
import os

POSTGRES_DB = os.environ.get("POSTGRES_DB", "rwdb")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", "5432")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "172.16.2.234")

CONNECTION_STR = f"host={POSTGRES_HOST} dbname={POSTGRES_DB} password={POSTGRES_PASSWORD} user={POSTGRES_USER}"

try:
    conn = psycopg2.connect(CONNECTION_STR)
    conn.close();
    print("Success!")
except psycopg2.OperationalError as ex:
    print("Connection failed: {0}".format(ex))
