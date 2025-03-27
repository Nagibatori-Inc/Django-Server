#!/bin/bash

# docker compose
function task:dc {
  docker compose -f "compose.yaml" "$@"
}

# docker compose exec
function task:dce {
  task:dc exec app "$@"
}

# docker compose build
function task:build {
  task:dc build
}

# docker compose up
function task:run {
  task:dc up -d --remove-orphans
}

# docker compose down
function task:down {
  task:dc down --remove-orphans
}

# manage.py shortcut
function task:manage {
  task:dce poetry run python manage.py "$@"
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

  task:build

  task:manage migrate

  (
    source ./.env
    task:manage createsuperuser --no-input
  )

  task:down
}

# run tests (TODO)
function task:test {
  # TODO Добавить сюда таску по запуску тестов, когда они появятся
  echo "Tests"
}

# run linters
function task:lint {
  task:dce black . --diff --color
  task:dce mypy .
  task:dce ruff check .
}

# run linters with autofix
function task:lint_and_fix {
  task:dce black .
  task:dce mypy .
  task:dce ruff
}

# show all tasks
function task:help {
  compgen -A function
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