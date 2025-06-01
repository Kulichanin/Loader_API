from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
from os.path import join, dirname
from os import environ

dotenv_path = join(dirname(__file__), 'env')
load_dotenv(dotenv_path)


class Database:
    _pool = None

    @classmethod
    def initialize(cls):
        if cls._pool is None:
            cls._pool = ConnectionPool(
                conninfo=f"""
                    host={environ.get('DB_HOST')}
                    port={environ.get('DB_PORT')}
                    dbname={environ.get('DB_NAME')}
                    user={environ.get('DB_USER')}
                    password={environ.get('DB_PASSWORD')}
                """,
                min_size=1,
                max_size=10
            )

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.initialize()
        return cls._pool.getconn()

    @classmethod
    def return_connection(cls, conn):
        cls._pool.putconn(conn)

    @classmethod
    def execute(cls, query, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount
        finally:
            cls.return_connection(conn)

    @classmethod
    def fetchval(cls, query, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                result = cur.fetchone()
                return result[0] if result else None
        finally:
            cls.return_connection(conn)

    @classmethod
    def fetchall(cls, query, params=None):
        conn = cls.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                columns = [desc[0]
                           for desc in cur.description]  # Получаем названия колонок
                results = cur.fetchall()
                # Преобразуем в список словарей
                return [dict(zip(columns, row)) for row in results]
        finally:
            cls.return_connection(conn)

    @classmethod
    def close_all(cls):
        if cls._pool:
            cls._pool.closeall()
