# VehicleBoard Backend

## Описание

## Деплой

Деплой осуществляется при пуше в ветку `dev`

## Как развернуть

Разворачивание проекта
1. Установить docker, docker compose
2. Установить pre-commit
3. Инициализация проекта: 
```sh
./Taskfile.sh init
```
4. Запуск проекта через docker compose:
```sh
./Taskfile.sh run
```

## Полезные команды

Запуск тестов:
```sh
./Taskfile.sh test
```

Запуск линтеров:
```sh
./Taskfile.sh lint
```


Для разворачивания отдельно контейнеров с СУБД PostgreSQL и ее ВЕБ интерфейсом pgadmin запусти
```sh
docker compose -f compose.db.yaml up --build
```
