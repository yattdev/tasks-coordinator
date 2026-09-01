#!/usr/bin/env bash
set -euo pipefail

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
fixture=${FIXTURE:-"$script_dir/artifacts/last_db.sql"}
if [[ -z "$(docker compose ps -q db)" ]]; then
  echo "Performcoop DB container is not running; start the task-owned Compose db service first." >&2
  exit 1
fi
if [[ ! -f "$fixture" ]]; then
  echo "Fixture is unavailable: $fixture" >&2
  exit 1
fi

docker compose exec -T db sh -eu -c '
  client=$(command -v mariadb || command -v mysql)
  : "${client:?MariaDB/MySQL client is unavailable}"
  : "${MYSQL_USER:?MYSQL_USER is unavailable in the DB container}"
  : "${MYSQL_PASSWORD:?MYSQL_PASSWORD is unavailable in the DB container}"
  : "${MYSQL_DATABASE:?MYSQL_DATABASE is unavailable in the DB container}"
  MYSQL_PWD="$MYSQL_PASSWORD" exec "$client" --user="$MYSQL_USER" "$MYSQL_DATABASE"
' < "$fixture"
