#!/bin/sh
set -eu
python tools/backup-database.py
python manage.py migrate --noinput
python manage.py import_market_prices
set --
if [ "${FASAL_TRUST_PROXY:-0}" = "1" ]; then
    set -- --trusted-proxy="${FASAL_PROXY_IP:?Set the trusted HTTPS proxy IP}" --trusted-proxy-headers=x-forwarded-proto
fi
exec waitress-serve --listen="0.0.0.0:${PORT:-8000}" --threads=4 "$@" fasal.wsgi:application
