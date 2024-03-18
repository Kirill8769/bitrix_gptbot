import logging
import os

import asyncpg
from dotenv import load_dotenv


class ChatDB:
    """
    Класс для взаимодействия с базой данных.
    """

    def __init__(self) -> None:
        load_dotenv()
        self._connection = None
        self.__host = os.getenv("HOST")
        self.__database = os.getenv("DATABASE")
        self.__user = os.getenv("USERNAME")
        self.__password = os.getenv("PASSWORD")
        logging.info("Database is activated")

    async def connect(self) -> None:
        """
        Устанавливает соединение с базой данных.
        """
        try:
            self._connection = await asyncpg.connect(
                host=self.__host, database=self.__database, user=self.__user, password=self.__password
            )
        except Exception as ex:
            logging.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)

    async def create_tables(self) -> None:
        """
        Создает таблицу в базе данных, если она не существует.
        """
        await self.connect()
        await self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS dialogs(
                ID SERIAL PRIMARY KEY,
                MANAGER_ID INT NOT NULL,
                PORTAL_USER_NAME VARCHAR(256),
                QUESTION TEXT,
                ANSWER TEXT,
                STATUS VARCHAR(16)
            )
                                """
        )
        await self._connection.close()

    async def save_question(self, data: dict) -> int:
        await self.connect()
        record_id = await self._connection.fetchval(
            """
            INSERT INTO dialogs (MANAGER_ID, PORTAL_USER_NAME, QUESTION)
            VALUES ($1, $2, $3)
            RETURNING ID
            """,
            data["id"],
            data["title"],
            data["text"],
        )
        await self._connection.close()
        return record_id

    async def save_answer(self, record_id: int, message: str, status: str) -> None:
        await self.connect()
        await self._connection.execute(
            """
            UPDATE dialogs SET ANSWER = $1, STATUS = $2
            WHERE ID = $3
            """,
            message,
            status,
            record_id,
        )
        await self._connection.close()
