# Репозитории

1. Auth-сервис [https://github.com/latiennetendresse/Auth_sprint_1](https://github.com/artitalk50/Auth_sprint_2)
2. Сервис выдачи контента [https://github.com/latiennetendresse/Async_API_sprint_2](https://github.com/artitalk50/Async_API_sprint_2)
3. Админка [https://github.com/latiennetendresse/new_admin_panel_sprint_3](https://github.com/artitalk50/new_admin_panel_sprint_2)

# Запуск приложения

Скопируйте `.env.example` в `.env` и задайте свои значения переменных окружения.

Для запуска auth-service, PostgreSQL, Redis, Nginx и Jaeger можно использовать команду:

`docker compose up --build`

После запуска должна открываться страница с документацией [http://127.0.0.1/api/openapi](http://127.0.0.1/api/openapi)

Для добавления пользователя с ролью `admin` из консоли можно воспользоваться командой:

`docker exec -it -e PYTHONPATH=. auth_sprint_2-auth-service-1 python cli/create_admin.py`

# Запуск тестов

Для запуска всех тестов можно использовать команду:

`docker compose -f auth-service/tests/functional/docker-compose.yml --env-file .env up --build --abort-on-container-exit --exit-code-from tests`

Для запуска отдельных тестов можно указать файл или конкретный тест при помощи переменной `TESTS`, например:

`TESTS=src/test_register.py::test_register docker compose -f auth-service/tests/functional/docker-compose.yml --env-file .env up --build --abort-on-container-exit --exit-code-from tests`

# Трассировка

После запуска интерфейс Jaeger будет доступен по ссылке [http://127.0.0.1:16686](http://127.0.0.1:16686)

Пример фильтра для поиска по request_id: 

`http.request.header.x_request_id=('412c25d48bb61b562e5e8ca1f27b304b',)`

# Процесс разработки

## Зависимости

Зависимости в [auth-service/requirements](auth-service/requirements) разделены на базовые [base.txt](auth-service/requirements/base.txt) (необходимые для работы сервиса) и дополнительные, используемые в процессе разработки.

Для установки полного набора можно использовать команду:

`pip install -r auth-service/requirements/dev.txt`

Зависимости для запуска тестов хранятся отдельно:

`pip install -r auth-service/tests/functional/requirements.txt`

## Проверки кода

Для автоформатирование используем [Black](https://github.com/psf/black):

`black .`

В качестве линтенра используем [Flake8](https://github.com/PyCQA/flake8):

`flake8`

Для сортировки импортов используем [isort](https://github.com/PyCQA/isort):

`isort .`

Для установки автоматических проверок кода (black, flake8, isort) перед коммитом можно использовать [pre-commit](https://pre-commit.com/):

`pre-commit install`

## Миграции PostgreSQL

Для работы с миграциями используется [Alembic](https://alembic.sqlalchemy.org/). 

Миграции хранятся в папке [auth-service/src/alembic/versions](auth-service/src/alembic/versions).

Создать новую миграцию миграцию можно следующим образом:

```bash
# Запустить Postgres
docker run -d --name postgres -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=db postgres:13.10-alpine

cd auth-service/src

# Применить уже имеющиеся миграции
alembic upgrade head
# Сгенерировать заготовку под новую миграцию
alembic revision --autogenerate -m "message"
```

Дальше надо посмотреть и при необходимости доработать автоматически созданную миграцию, как описано в [документации Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html). 

# Проектная работа 7 спринта

1. Создайте интеграцию Auth-сервиса с сервисом выдачи контента и панелью администратора Django, используя контракт, который вы сделали в прошлом задании.
  
    При создании интеграции не забудьте учесть изящную деградацию Auth-сервиса. Как вы уже выяснили ранее, Auth сервис один из самых нагруженных, потому что в него ходят большинство сервисов сайта. И если он откажет, сайт отказать не должен. Обязательно учтите этот сценарий в интеграциях с Auth-сервисом.
2. Добавьте в Auth трасировку и подключите к Jaeger. Для этого вам нужно добавить работу с заголовком x-request-id и отправку трасировок в Jaeger.
3. Добавьте в сервис механизм ограничения количества запросов к серверу.
4. Упростите регистрацию и аутентификацию пользователей в Auth-сервисе, добавив вход через социальные сервисы. Список сервисов выбирайте исходя из целевой аудитории онлайн-кинотеатра — подумайте, какими социальными сервисами они пользуются. Например, использовать [OAuth от Github](https://docs.github.com/en/free-pro-team@latest/developers/apps/authorizing-oauth-apps){target="_blank"} — не самая удачная идея. Ваши пользователи не разработчики и вряд ли имеют аккаунт на Github. А вот добавить VK, Google, Yandex или Mail будет хорошей идеей.

    Вам не нужно делать фронтенд в этой задаче и реализовывать собственный сервер OAuth. Нужно реализовать протокол со стороны потребителя.
    
    Информация по OAuth у разных поставщиков данных: 
    
    - [Yandex](https://yandex.ru/dev/oauth/?turbo=true){target="_blank"},
    - [VK](https://vk.com/dev/access_token){target="_blank"},
    - [Google](https://developers.google.com/identity/protocols/oauth2){target="_blank"},
    - [Mail](https://api.mail.ru/docs/guides/oauth/){target="_blank"}.
    
## Дополнительное задание
    
Реализуйте возможность открепить аккаунт в соцсети от личного кабинета. 
    
Решение залейте в репозиторий текущего спринта и отправьте на ревью.
