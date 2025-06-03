# Loader_API

Реализовать API для WEB приложение, которое будет получать данные для загрузки файла и дальнейшей обработки в системе.

## Алгоритм работа

Перед запуском приложения необходимо переименовать файл `env.example` в `env` и задать данные для подключения к postgres.

Создать виртуальное окружение для Python, активировать окружение и установить зависимости.

```bash
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

Проверим подключение к бд с помощью [pg_isready](https://www.postgresql.org/docs/current/app-pg-isready.html)

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

## Документация

Вы можете увидите автоматическую интерактивную документацию API. (Создано с помощью [Swagger-ui](https://github.com/swagger-api/swagger-ui))

```bash
http://127.0.0.1:8000/docs
```

Другой вариант документации. (Создано с помощью [Redoc](https://github.com/Redocly/redoc))

## Тестирование

Тестирование проводилось в [Postman](https://www.postman.com/). Файл `.test/Loader_api.postman_collection.json` использовать для Postman 2.1+.Также для удобства подготовлен файл для [EchoAPI](https://www.echoapi.com/download). Файл `.test/Loader_Api_echoapi.json`

## Сбока в Docker Image

Сборка образа оптимизирована с примемами из статьи [Docker Best Practices for Python Developers](https://testdriven.io/blog/docker-best-practices/)

Docker кэширует каждый шаг (или слой) в определенном Dockerfile для ускорения последующих сборок. При изменении шага кэш будет аннулирован не только для этого конкретного шага, но и для всех последующих шагов.

В этом Dockerfile скопирован код приложения перед установкой требований. Теперь, каждый раз, когда мы изменяем код приложения, сборка будет переустанавливать пакеты. Это очень неэффективно, особенно при использовании контейнера Docker в качестве среды разработки. Поэтому крайне важно сохранять файлы, которые часто изменяются, ближе к концу Dockerfile.

Поэтому сначала слои установки окружения для приложения, а только потом копирования приложения

```dockerfile
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host $IP_SERVICE --port $PORT_SERVICE"]
```

По умолчанию Docker запускает процессы контейнера как root внутри контейнера. Однако это плохая практика, поскольку процесс, запущенный как root внутри контейнера, запущен как root на хосте Docker.

Поэтому добавим создание пользователя и запуск через него приложения

```dockerfile
RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app
```

## Запуск и взаимодействие с Docker Image

Сборка образа

```bash
docker build -t kdv/loader_api .
```

Запуск образа

```bash
docker run -d -p 8000:8000 --name loader_api kdv/loader_api:latest
```

Также для тестов подготовлен docker compose файл `.infra/docker-compose.yaml` с которым поднимается сразу проект с БД

Запуск через docker compose

```bash
docker compose --env-file env -f .infra/docker-compose.yaml up -d 
```

Обратить внимание! Если есть желание пробросить папку заранее с файлами на хостовую машину, необходимо после запуска docker compose изменить права на эту папку, иначе файлы сохраняться не будут и будет выскакивать ошибка следующего вида

```json
{
    "detail": "Error saving file: [Errno 13] Permission denied: '/loader/uploads/0d5d401b-75f3-4a2f-a07a-d259e533a4cb.pdf'"
}
```

Измение прав доступа на каталог

```bash
sudo chmod -R 777 uploads/
```

## Улучшения для production

* Использовать переменные docker для конфигурации БД
* Добавить обработку ошибок подключения к БД
* Реализовать миграции базы данных (например, с помощью Alembic)
* Добавить логирование
* Реализовать аутентификацию/авторизацию
* Добавить лимиты на размер загружаемых файлов
