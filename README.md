# Loader_API

Реализовать API для WEB приложение, которое будет получать данные длдя загрузки файла и дальнейшей обработки в системе.

## Алгоритм работа

Перед запуском приложения необходимо переименовать файл `env.example` в `env` и задать данные для подключения к postgres.

Создать виртуальное окружение для Python, активировать окружение и установить зависимости.

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Проверим подключение к бд

```bash
pg_isready -d <db_name> -h <host_name> -p <port_number> -U <db_user>  
```

Запустить приложение в `dev` моде.

```bash
fastapi dev main.py
```

Вывод при успешном запуске

```bash
   FastAPI   Starting development server 🚀
 
             Searching for package file structure from directories with __init__.py files
             Importing from /home/mda/Project/Loader_API
 
    module   🐍 main.py
 
      code   Importing the FastAPI app object from the module with the following code:
 
             from main import app
 
       app   Using import string: main:app
 
    server   Server started at http://127.0.0.1:8000
    server   Documentation at http://127.0.0.1:8000/docs
 
       tip   Running in development mode, for production use: fastapi run
 
             Logs:
 
      INFO   Will watch for changes in these directories: ['/home/mda/Project/Loader_API']
      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
      INFO   Started reloader process [33094] using WatchFiles
      INFO   Started server process [33102]
      INFO   Waiting for application startup.
      INFO   Application startup complete.
```

Просмотреть документацию

```bash
http://127.0.0.1:8000/docs
```

## Тестирование

Тестирование проводилось в Postman. Файл `postman/Loader_api.postman_collection.json` использовать для Postman 2.1+.

## Сбока в Docker Image

Тут будет текст

## Запуск и взаимодействие с Docker Image

Тут будет текст

## Улучшения для production

* Использовать переменные docker для конфигурации БД
* Добавить обработку ошибок подключения к БД
* Реализовать миграции базы данных (например, с помощью Alembic)
* Добавить логирование
* Реализовать аутентификацию/авторизацию
* Добавить лимиты на размер загружаемых файлов
