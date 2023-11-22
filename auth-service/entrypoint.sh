#!/usr/bin/env bash
set -e

alembic upgrade head

gunicorn main:app --bind 0.0.0.0:8000 -w ${WORKERS:-1} -k uvicorn.workers.UvicornWorker
