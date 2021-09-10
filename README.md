# Микросервис Auth
## Архитектура
В качестве веб-сервера используется caddy, как наиболее простой в настройке, но в тоже время и функциональный.
Основное хранилище данных — Postgres, для хранения сессий используется Redis.
![Alt text](https://erdyakov.notion.site/image/https%3A%2F%2F316129.selcdn.ru%2Fpublic%2Fdiagram.png?table=block&id=bc0585ff-85c0-4eff-a1b3-421996ad722f&spaceId=adc1ac53-04a0-4cc7-b2aa-dd8d81f6dc5e&userId=&cache=v2 "a title")
## Демо
https://yandex.in.net
## Запуск приложения в проде
1. Скопировать файл конфигурации
```shell
cat config/.env.template > config/.env
````
2. В файле `config/.env` заполнить секреты данными.
3. Запустить контейнеры.
```shell
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```
## Запуск приложения локально
1. Скопировать файл конфигурации
```shell
cat config/.env.template > config/.env
````
2. В файле `config/.env` заполнить секреты данными.
3. Провести миграции.
```shell
docker-compose run --rm flask-api flask db upgrade
```
4. Запустить контейнеры.
```shell
docker-compose up
```
5. Перейти в браузере по адресу `0.0.0.0:8000`.
## Запуск тестов
```shell
docker-compose run --rm flask-api pytest
```

