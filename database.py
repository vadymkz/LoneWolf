import sqlite3

from pathlib import Path
from contextlib import contextmanager
from models import Vacancy
from settings import BASE_DIR

DB_PATH = BASE_DIR / Path("sqlite.db")


@contextmanager
def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_tables() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                posted_at TEXT,
                title TEXT,
                description TEXT,
                link TEXT,
                company TEXT,
                source TEXT,
                salary TEXT,
                checked INTEGER DEFAULT 0
            )
            """)
        conn.commit()


def get_vacancies(source: str) -> list:
    query = f"SELECT * FROM vacancies WHERE source='{source}'"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        vacancies = cursor.fetchall()
    return vacancies


def insert_vacancies(vacancies: list[Vacancy]):
    with get_connection() as conn:
        cursor = conn.cursor()
        values = [vacancy.to_tuple() for vacancy in vacancies]
        cursor.executemany("""
            INSERT INTO vacancies (
                posted_at,
                title,
                description,
                link,
                company,
                source,
                salary,
                checked
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, values)
        conn.commit()
