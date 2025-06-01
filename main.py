# FastAPI— это класс Python, который предоставляет все функциональные возможности вашего API.
from typing import Annotated
from fastapi import FastAPI, HTTPException, UploadFile, Header, Request, status
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database import Database
from typing import AsyncIterator
from uuid import uuid4
from dotenv import load_dotenv
from os.path import join, dirname, splitext, join, exists
from os import environ, makedirs, remove


dotenv_path = join(dirname(__file__), 'env')
load_dotenv(dotenv_path)


class FileRecord(BaseModel):
    file_id: str
    file_name: str
    file_path: str


class DeleteFileRequest(BaseModel):
    file_id: str


# Получаем путь для загрузки из переменных окружения
PATH_DOWNLOAD = environ.get('PATH_DOWNLOAD', './uploads')

# Создаем директорию, если ее нет
makedirs(PATH_DOWNLOAD, exist_ok=True)

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
app = FastAPI(lifespan=lifespan)


# Создаем URL для обрещения с определением метода(POST, GET, PUT, DELETE).
# Путь здесь относится к последней части URL-адреса, начинающейся с первой /.
# Определяем декоратор операции пути.


@app.get("/")
# 1. GET / - Проверка статуса сервера
def get_server_status(request: Request) -> dict:
    user_agent = request.headers.get("user-agent")
    return {"status": "running", "framework": "FastAPI", "User-Agent": user_agent}


@app.post("/loader")
# 2. POST /loader - Загрузка файла
def upload_file(file: UploadFile):
    # Типы файлов доступные для загрузки
    allowed_content_types = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Only PDF and DOC/DOCX are allowed."
        )

    # Генерируем уникальный ID и путь для файла
    file_id = str(uuid4())
    file_extension = splitext(file.filename)[1]
    file_path = join(PATH_DOWNLOAD, f"{file_id}{file_extension}")

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


@app.get("/files", response_model=list[FileRecord])
# 3. GET /files - список всех файлов
def get_all_files():
    """Возвращает список всех файлов в базе данных"""
    files = Database.fetchall(
        "SELECT file_id, file_name, file_path FROM files ORDER BY file_name"
    )
    return files


@app.delete("/delete_file/{file_id}")
# 4. DELETE /delete_file - Удаление файла по ID
def delete_file(file_id: str):
    """
    Удаляет файл по его ID.
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
