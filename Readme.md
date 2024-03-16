# Refferal App

RESTful API сервис для реферальной системы.

### Технологии

- [FastApi](https://fastapi.tiangolo.com/). Для реализации backend-а сервиса;
- [SqlAlchemy](https://www.sqlalchemy.org/) ORM. Для реализации моделей для хранения данных сервиса;
- [SQLite](https://www.sqlite.org/). База Данных сервиса;
- [JWT](https://jwt.io/). Реализая аутентификации и реферальной системы.

### Запуск

1. Клонируйте репозиторий
   командой: `git clone https://github.com/Surzhikov161/Refferal-App.git`
2. Установите [Docker](https://docs.docker.com/engine/install/), если у вас его нет;
3. Создайте .env файл командой: `cp .env.template .env`;
4. Настроить параметры окружения в файле .env;
5. Запустите приложение командой: `docker compose up -d`.

### Тестирование:

1. Из корневой папки запустите тесты командой: `pytest tests`;
