import asyncio
import threading

from celery import Celery

from db.db_handlers import ChatDB
from gpt_free_bot import ChatBot
from loggers import logger
from src.bitrix_chat import BitrixChat
from src.utils import restart_program

app = Celery("tasks", broker="redis://localhost:6379/0")
app.conf.broker_connection_retry_on_startup = True


@app.task
async def process_chat_message(chat: dict) -> None:
    """
    Обрабатывает сообщение в чате, получает ответ от чат-бота, отправляет ответ в чат и обрабатывает ошибки.

    :params chat: Словарь с сообщением и данными отправителя.
    """
    chat_db = ChatDB()
    chat_bot = ChatBot()
    bit_handler = BitrixChat()
    record_id = await chat_db.save_question(data=chat)
    logger.info(f'[Q] {chat["title"]}: Задал вопрос боту')

    bot_answer = await chat_bot.get_response_gpt(chat["text"])

    while True:
        send = await bit_handler.send_message(chat["id"], bot_answer)
        if send:
            await chat_db.save_answer(record_id=record_id, message=bot_answer, status="[OK]")
            logger.info(f'[A] {chat["title"]}: Бот ответил')
            break
        else:
            bit_handler.count += 1
            await chat_db.save_answer(record_id=record_id, message="Ошибка ответа", status="[ERROR]")
            logger.error(f'[A] {chat["title"]}: Ошибка ответа {bit_handler.count}')
            await bit_handler.send_message(
                bit_handler.admin_id, f'[Error] Ошибка обработки запроса от пользователя: {chat["title"]}'
            )
            if bit_handler.count >= 3:
                logger.error(f'[A] {chat["title"]}: Попытки отправки ответа не увенчались успехом')
                break


async def process_all_chats(chats: list) -> None:
    """
    Обрабатывает все чаты одновременно.

    :params chats: Список чатов для обработки.
    """
    tasks = []
    for chat in chats:
        task = asyncio.create_task(process_chat_message(chat))
        tasks.append(task)
    await asyncio.gather(*tasks)


async def main() -> None:
    """
    Основная функция, которая выполняет циклическую обработку сообщений в чатах.
    """
    bit_handler = BitrixChat()
    chat_db = ChatDB()
    await chat_db.create_tables()
    count = 0
    while True:
        count += 1
        if count >= 700:
            restart_program()
        chats = await bit_handler.get_all_chat()
        await process_all_chats(chats)
        await asyncio.sleep(2)


if __name__ == "__main__":
    main_thread = threading.Thread(target=asyncio.run, args=(main(),))
    main_thread.start()
    app.worker_main(["worker"])
