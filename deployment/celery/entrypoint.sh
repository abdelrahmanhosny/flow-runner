#!/bin/bash

function postgres_ready(){
python << END
import sys
import psycopg2
import environ
try:
    ROOT_DIR = environ.Path(__file__) - 3
    APPS_DIR = ROOT_DIR.path('src')
    ENV_PATH = str(APPS_DIR.path('.env'))
    env = environ.Env()
    if env.bool('READ_ENVFILE', default=True):
        env.read_env(ENV_PATH)
    conn = psycopg2.connect(dbname=env('POSTGRES_DB', default=''), user=env('POSTGRES_USER', default=''), password=env('POSTGRES_PASSWORD', default=''), host="postgres")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."

# source Timberwolf environment
orig_dir=`pwd`
cd /home/bill/openroad.release
source setenv.sh
cd /home/bill/openroad.release/bin/itools.2.0.0pre43omega20z5
source setenv.sh
cd $orig_dir

# start celery worker
celery -A flow worker -l info

