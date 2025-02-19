# --PROJECT NAME--

## Описание

## Деплой

### Продакшн

На момент 18.02.25, чтобы развернуть приложение, достаточно двух команд
```sh
docker compose build
```

И

```sh
docker compose up
```

Но есть и маленькая альтернатива (что я бы советовал применять)
```sh
docker compose up --build
```

> [!CAUTION]
> Если в процессе сборки целиком всех контейнеров возникнет ошибка следующего рода
> ```
> [+] Running 0/0
[+] Running 0/1 Building                                                                                                     0.1s 
[+] Building 2.1s (5/10)                                                                                           docker:default 
 => [app internal] load build definition from Dockerfile                                                                     0.0s
 => => transferring dockerfile: 352B                                                                                         0.0s
 => [app internal] load metadata for docker.io/library/python:3.7-alpine                                                     1.8s 
 => [app internal] load .dockerignore                                                                                        0.0s
 => => transferring context: 2B                                                                                              0.0s
 => [app 1/6] FROM docker.io/library/python:3.7-alpine@sha256:f3d31c8677d03f0b3c724446077f229a6ce9d3ac430f5c08cd7dff0029204  0.0s
 => ERROR [app internal] load build context                                                                                  0.1s
 => => transferring context: 135.47kB                                                                                        0.0s 
------
[+] Running 0/1l] load build context:
 ⠹ Service app  Building                                                                                                     2.2s 
failed to solve: error from sender: open /home/anton/Projects/University/Diploma/Django-Server/.postgres_data: permission denied
> ```
> Просто запуститесборку проекта как sudo user: `sudo docker compose up --build` 
> или сразу под рутом `sudo -i` и после уже `docker compose up --build`

Эта команда сразу и собирает (если уже собраны, то пересобирает) контейнеры и запускает их (дальше все будет через нее)

### Разработка

Для разворачивания отдельно контейнеров с СУБД PostgreSQL и ее ВЕБ интерфейсом pgadmin запусти
```sh
docker compose -f compose.db.yaml up --build
```

Если нужен отдельно Django, дерзай
```sh
docker compose -f а_хуй_там_пока_не_написал_файл up --build
```
