#!/bin/bash

function task:d {
  docker "$@"
}

# docker compose
function task:dc {
  task:d compose -f "compose.yaml" "$@"
}

# docker compose exec
function task:de {
  container_name="$1"
  shift

  if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
    task:d exec "$container_name" "$@"
  else
    echo "Container $container_name is not running"
    exit 1
  fi
}

# docker compose build
# shellcheck disable=SC2120
function task:build {
  task:dc build "$@"
}

# docker compose up
function task:run {
  task:dc up -d
}

# docker compose down
function task:down {
  task:dc down -v
}

# docker system prune -f
function task:clean {
  docker system prune -f
}

# poetry shortcut
function task:poetry {
  task:de vehicle_board_api poetry "$@"
}

# manage.py shortcut
function task:manage {
  task:poetry run python manage.py "$@"
}

# docker compose up --build + migrate
function task:deploy {
  task:build
  task:run
  task:manage migrate
}

# init project script
function task:init {
  if [[ ! $(pre-commit --version) ]]; then
    echo "Error: pre-commit not found"
    exit 1;
  fi

  pre-commit install \
      --hook-type pre-commit \
      --hook-type pre-push \
      --hook-type commit-msg

  task:deploy

  (
    source ./.env

    if [[ ! $DJANGO_SUPERUSER_USERNAME || ! $DJANGO_SUPERUSER_PASSWORD ]]; then
      echo "Cannot find DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD env variables."
      echo "Create .env file with DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD variables in project root dir."
      exit 1
    fi
    task:manage createsuperuser --no-input
    task:manage create_default_adverts
  )

  task:down
}

# docker system prune + down + build + run + migrate
function task:rebuild {
  task:clean
  task:down
  task:deploy
}

# run tests
function task:test {
  task:run
  task:de vehicle_board_api pytest .
  task:down
}

# run linters
function task:lint {
  task:de vehicle_board_api black . --diff --color
  task:de vehicle_board_api mypy .
  task:de vehicle_board_api ruff check .
}

# run linters with autofix
function task:lint-and-fix {
  task:de vehicle_board_api black . --color
  task:de vehicle_board_api mypy .
  task:de vehicle_board_api ruff check --fix
}

# show all tasks
function task:help {
  echo "Available tasks:"
  compgen -A function
}

function task:pytest_pre_commit_hook {
  task:run

  task:de vehicle_board_api pytest . 2>&1
  exit_code=$?

  task:down

  exit $exit_code
}

task="task:$1"
shift

if declare -f "$task" > /dev/null; then
  "$task" "$@"
else
  echo "Error: Task '$task' not found."
  task:help
  exit 1
fi