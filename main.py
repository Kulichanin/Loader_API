# FastAPI— это класс Python, который предоставляет все функциональные возможности вашего API.
from ast import AnnAssign
from fastapi import FastAPI, HTTPException, UploadFile, File, Path, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database import Database
from typing import AsyncIterator, Annotated
from uuid import uuid4
from dotenv import load_dotenv
from os.path import join, dirname, splitext, join, exists
from os import environ, makedirs, remove


dotenv_path = join(dirname(__file__), 'env')
load_dotenv(dotenv_path)

class HealthCheck(BaseModel):
    status: str = "OK"

class FileRecord(BaseModel):
    file_id: str = "b4dbcf94-ad7f-4f0c-b083-47d0af530a6b"
    file_name: str = "test.pdf"
    file_path: str = "/loader/uploads/b4dbcf94-ad7f-4f0c-b083-47d0af530a6b.pdf"

class DeleteFile(BaseModel):
    file_id: str = "b4dbcf94-ad7f-4f0c-b083-47d0af530a6b"

# Получаем путь для загрузки из переменных окружения
PATH_DOWNLOAD = environ.get("PATH_DOWNLOAD", "/uploads")

# Создаем директорию, если ее нет
makedirs(dirname(__file__)+PATH_DOWNLOAD, exist_ok=True)

# Типы файлов доступные для загрузки
allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

# Инициализация таблицы и проверка подключения к БД.
# В реальном приложении создание таблицы делается через миграции (например, с помощью Alembic)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup code
    Database.initialize()
    Database.execute("""
        CREATE TABLE IF NOT EXISTS files (
            file_id TEXT PRIMARY KEY,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield
    # Shutdown code
    Database.close_all()


# Здесь appпеременная будет «экземпляром» класса FastAPI.
# Это будет основная точка взаимодействия при создании всего вашего API.
app = FastAPI(lifespan=lifespan, title="Loader API", summary="Example of api work for file upload ", version="0.7")


# Создаем URL для обрещения с определением метода(POST, GET, PUT, DELETE).
# Путь здесь относится к последней части URL-адреса, начинающейся с первой /.
# Определяем декоратор операции пути.

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
# 1. GET /health - Проверка статуса сервера
def get_health():
    """
    ## Выполнить проверку работоспособности
    Конечная точка для проверки работоспособности. Эта конечная точка может в первую очередь использоваться Docker
    для обеспечения надежной оркестровки и управления контейнерами. Другие
    службы, которые полагаются на правильное функционирование службы API, не будут развернуты, если эта
    конечная точка возвращает любой другой код состояния HTTP, кроме 200 (OK).
    Возвращает:
        HealthCheck: возвращает ответ JSON со статусом работоспособности
    """
    return HealthCheck(status="OK")

@app.post("/loader", tags=["loader_api"], response_model=FileRecord) 
# 2. POST /loader - Загрузка файла
def upload_file(file: Annotated[UploadFile, File(description="Поле, которое будет обработано для загрузки файла", media_type=allowed_content_types)]):
    """
    Загружает файл на сервер и записывает данные о нем в БД.
    Возвращает:
        JSON: возвращает ответ JSON с данным про файл
    """
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only PDF and DOC/DOCX are allowed."
        )

    # Генерируем уникальный ID и путь для файла
    file_id = str(uuid4())
    file_extension = splitext(file.filename)[1]
    file_path = join(dirname(__file__)+PATH_DOWNLOAD, f"{file_id}{file_extension}")

    # Сохраняем файл на диск
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )

    # Сохраняем информацию о файле в БД
    Database.execute(
        "INSERT INTO files (file_id, file_name, file_path) VALUES (%s, %s, %s)",
        (file_id, file.filename, file_path)
    )

    return {
        "file_id": file_id,
        "file_name": file.filename,
        "file_path": file_path
    }


@app.get("/files", tags=["loader_api"], response_model=list[FileRecord])
# 3. GET /files - список всех файлов
def get_all_files() -> list[FileRecord]:
    """
    Список всех файлов в базе данных.
    Возвращает:
        JSON: возвращает ответ JSON с списков файлов
    """
    files = Database.fetchall(
        "SELECT file_id, file_name, file_path FROM files ORDER BY file_name"
    )
    return files


@app.delete("/delete_file/{file_id}", tags=["loader_api"], response_model=DeleteFile)
# 4. DELETE /delete_file - Удаление файла по ID
def delete_file(file_id: Annotated[str, Path(title="file_id", description="Значение file_id файла, которые нужно удалить")]):
    """
    Удаляет файл по его ID.
    Возвращает:
        JSON: возвращает ответ JSON с file_id и названием файла
    """
    file_info = Database.fetchall(
        "SELECT file_name, file_path FROM files WHERE file_id = %s",
        (file_id,)
    )

    if not file_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )

    file_name = file_info[0]['file_name']
    file_path = file_info[0]['file_path']

    try:
        if exists(file_path):
            remove(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting file: {str(e)}"
        )

    Database.execute(
        "DELETE FROM files WHERE file_id = %s",
        (file_id,)
    )

    return {"deleted_file": file_name}
