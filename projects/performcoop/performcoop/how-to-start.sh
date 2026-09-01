#!/usr/bin/env bash
set -euo pipefail

: "${COMPOSE_PROJECT_NAME:?Set a unique task-owned COMPOSE_PROJECT_NAME}"
: "${DB_PORT:?Set a unique task-owned DB_PORT}"
: "${WEB_PORT:?Set a unique task-owned WEB_PORT}"

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_root=${PROJECT_ROOT:-$PWD}
cd "$project_root"

docker compose up -d db
for _ in $(seq 1 90); do
  if docker compose exec -T db sh -eu -c '
    client=$(command -v mariadb || command -v mysql)
    : "${client:?MariaDB/MySQL client is unavailable}"
    : "${MYSQL_USER:?MYSQL_USER is unavailable in the DB container}"
    : "${MYSQL_PASSWORD:?MYSQL_PASSWORD is unavailable in the DB container}"
    : "${MYSQL_DATABASE:?MYSQL_DATABASE is unavailable in the DB container}"
    MYSQL_PWD="$MYSQL_PASSWORD" "$client" --user="$MYSQL_USER" --execute="SELECT 1" "$MYSQL_DATABASE" >/dev/null
  ' >/dev/null 2>&1; then
    db_ready=yes
    break
  fi
  sleep 1
done
if [[ "${db_ready:-no}" != yes ]]; then
  echo "Task-owned Performcoop DB did not become ready within 90 seconds." >&2
  exit 1
fi

FIXTURE="${FIXTURE:-$script_dir/artifacts/last_db.sql}" \
  "$script_dir/how-to-load.sh"
docker compose up -d web
docker compose ps
