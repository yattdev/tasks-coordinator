#!/usr/bin/env bash
set -euo pipefail

: "${COMPOSE_PROJECT_NAME:?Set a unique task-owned COMPOSE_PROJECT_NAME}"
: "${DB_PORT:?Set a unique task-owned DB_PORT}"
: "${WEB_PORT:?Set a unique task-owned WEB_PORT}"

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
project_root=${PROJECT_ROOT:-$PWD}
cd "$project_root"

docker compose up -d db
container=$(docker compose ps -q db)
for _ in $(seq 1 90); do
  status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container")
  [[ "$status" == healthy || "$status" == running ]] && break
  sleep 1
done
status=$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container")
if [[ "$status" != healthy && "$status" != running ]]; then
  echo "Task-owned Performcoop DB did not become ready: $status" >&2
  exit 1
fi

MYSQL_CONTAINER="$container" FIXTURE="${FIXTURE:-$script_dir/artifacts/last_db.sql}" \
  "$script_dir/how-to-load.sh"
docker compose up -d web
docker compose ps
