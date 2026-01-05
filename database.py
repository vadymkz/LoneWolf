from pathlib import Path
from typing import AsyncGenerator
from contextlib import asynccontextmanager

import aiosqlite

from models import Vacancy
from settings import BASE_DIR

DB_PATH = BASE_DIR / Path("sqlite.db")


@asynccontextmanager
async def get_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def create_tables() -> None:
    async with get_connection() as conn:
        cursor = conn.cursor()
        await cursor.execute("""
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
        await conn.commit()


async def get_vacancies(source: str) -> list:
    query = f"SELECT * FROM vacancies WHERE source='{source}'"
    async with get_connection() as conn:
        cursor = await conn.cursor()
        await cursor.execute(query)
        vacancies = await cursor.fetchall()
    return vacancies


async def insert_vacancies(vacancies: list[Vacancy]):
    async with get_connection() as conn:
        cursor = await conn.cursor()
        values = [vacancy.to_tuple() for vacancy in vacancies]
        await cursor.executemany("""
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
        await conn.commit()
