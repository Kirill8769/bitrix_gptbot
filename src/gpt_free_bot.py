import asyncio
from random import randint

from freeGPT import AsyncClient

from loggers import logger


class ChatBot:
    """Класс для работы с ботом"""

    @staticmethod
    async def get_response_gpt(promt: str) -> str:
        """
        Метод делает запрос к боту и возвращает ответ.

        :param promt: Сообщение пользователя.
        :return: Ответ бота.
        """
        response = "Произошла ошибка, повторите пожалуйста ваш вопрос позже"
        try:
            if not isinstance(promt, str):
                raise ValueError("Для атрибута promt ожидается тип данных str")
            tmp_count = 0
            while True:
                if tmp_count >= 3:
                    raise UserWarning("Превышен допустимый лимит ошибок ответа на запрос")
                else:
                    try:
                        response = await AsyncClient.create_completion("gpt3", promt)
                        await asyncio.sleep(randint(5, 10))
                        break
                    except Exception as ex:
                        tmp_count += 1
                        logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
                        continue
        except UserWarning as user_ex:
            logger.warning(f"{user_ex.__class__.__name__}: {user_ex}")
        except Exception as ex:
            logger.debug(f"{ex.__class__.__name__}: {ex}", exc_info=True)
        finally:
            return response
