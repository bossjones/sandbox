#!/usr/bin/env bash
cd upscale_cli
mkdir -p db/{migrations,queries,repositories} || true
mkdir -p models/{domain,schemas} || true
mkdir -p resources || true
mkdir -p services || true
mkdir -p downloaders || true

# EG: https://github.com/bergran/places/blob/master/apps/places/generators/places.py
mkdir -p generators

touch db/__init__.py
touch db/migrations/__init__.py
touch db/queries/__init__.py
touch db/repositories/__init__.py


touch models/__init__.py
touch models/domain/__init__.py
touch models/schemas/__init__.py

touch resources/__init__.py
touch services/__init__.py
touch downloaders/__init__.py
cd -
